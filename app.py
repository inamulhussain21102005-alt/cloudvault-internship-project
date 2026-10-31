import os
import sqlite3
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
BACKUP_DIR = BASE_DIR / "backups"
DB_PATH = BASE_DIR / "cloud_storage.db"
ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx", "png", "jpg", "jpeg", "csv", "xlsx", "ppt", "pptx", "zip"}
MAX_FILE_BYTES = 20 * 1024 * 1024
USER_QUOTA_BYTES = 100 * 1024 * 1024

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-key")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_BYTES + 1024 * 1024

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )""")
        db.execute("""CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_name TEXT NOT NULL,
            size INTEGER NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            deleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )""")

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def user_usage(user_id, include_deleted=False):
    with get_db() as db:
        if include_deleted:
            row = db.execute("SELECT COALESCE(SUM(size),0) AS total FROM files WHERE user_id=?", (user_id,)).fetchone()
        else:
            row = db.execute("SELECT COALESCE(SUM(size),0) AS total FROM files WHERE user_id=? AND deleted=0", (user_id,)).fetchone()
    return int(row["total"])

def human_size(num):
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024 or unit == "GB":
            return f"{num:.1f} {unit}" if unit != "B" else f"{num} B"
        num /= 1024

@app.context_processor
def utility_context():
    return {"human_size": human_size, "quota_bytes": USER_QUOTA_BYTES}

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 8:
            flash("Username must be at least 3 characters and password at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with get_db() as db:
                db.execute("INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                           (username, generate_password_hash(password), datetime.now().isoformat(timespec="seconds")))
            flash("Account created. Please sign in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username is already taken.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    q = request.args.get("q", "").strip()
    with get_db() as db:
        if q:
            files = db.execute("""SELECT * FROM files WHERE user_id=? AND deleted=0
                AND original_name LIKE ? ORDER BY uploaded_at DESC""", (user_id, f"%{q}%")).fetchall()
        else:
            files = db.execute("SELECT * FROM files WHERE user_id=? AND deleted=0 ORDER BY uploaded_at DESC", (user_id,)).fetchall()
        count = db.execute("SELECT COUNT(*) AS n FROM files WHERE user_id=? AND deleted=0", (user_id,)).fetchone()["n"]
    usage = user_usage(user_id)
    return render_template("dashboard.html", files=files, count=count, usage=usage,
                           quota=USER_QUOTA_BYTES, query=q)

@app.route("/upload", methods=["POST"])
@login_required
def upload():
    file = request.files.get("file")
    if not file or not file.filename:
        flash("Choose a file to upload.", "error")
        return redirect(url_for("dashboard"))
    safe_name = secure_filename(file.filename)
    if not safe_name or not allowed_file(safe_name):
        flash("File type not allowed. Please choose a supported document, image, spreadsheet, presentation or ZIP file.", "error")
        return redirect(url_for("dashboard"))
    data = file.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        flash("Maximum file size is 20 MB.", "error")
        return redirect(url_for("dashboard"))
    if user_usage(session["user_id"]) + len(data) > USER_QUOTA_BYTES:
        flash("Your demo storage quota (100 MB) would be exceeded.", "error")
        return redirect(url_for("dashboard"))
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    (UPLOAD_DIR / stored_name).write_bytes(data)
    with get_db() as db:
        db.execute("""INSERT INTO files(user_id,original_name,stored_name,size,file_type,uploaded_at)
            VALUES(?,?,?,?,?,?)""",
            (session["user_id"], safe_name, stored_name, len(data),
             safe_name.rsplit(".", 1)[1].lower(), datetime.now().isoformat(timespec="seconds")))
    flash("File uploaded successfully.", "success")
    return redirect(url_for("dashboard"))

def get_owned_file(file_id, include_deleted=False):
    with get_db() as db:
        row = db.execute("SELECT * FROM files WHERE id=? AND user_id=?",
                         (file_id, session["user_id"])).fetchone()
    if not row or (row["deleted"] and not include_deleted):
        abort(404)
    return row

@app.route("/download/<int:file_id>")
@login_required
def download(file_id):
    row = get_owned_file(file_id)
    return send_from_directory(UPLOAD_DIR, row["stored_name"], as_attachment=True, download_name=row["original_name"])

@app.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    row = get_owned_file(file_id)
    with get_db() as db:
        db.execute("UPDATE files SET deleted=1 WHERE id=? AND user_id=?", (file_id, session["user_id"]))
    flash("File moved to Trash. You can restore it later.", "success")
    return redirect(url_for("dashboard"))

@app.route("/trash")
@login_required
def trash():
    with get_db() as db:
        files = db.execute("SELECT * FROM files WHERE user_id=? AND deleted=1 ORDER BY uploaded_at DESC",
                           (session["user_id"],)).fetchall()
    return render_template("trash.html", files=files)

@app.route("/restore/<int:file_id>", methods=["POST"])
@login_required
def restore(file_id):
    row = get_owned_file(file_id, include_deleted=True)
    if user_usage(session["user_id"]) + row["size"] > USER_QUOTA_BYTES:
        flash("Cannot restore: storage quota would be exceeded.", "error")
        return redirect(url_for("trash"))
    with get_db() as db:
        db.execute("UPDATE files SET deleted=0 WHERE id=? AND user_id=?", (file_id, session["user_id"]))
    flash("File restored.", "success")
    return redirect(url_for("trash"))

@app.route("/backup", methods=["POST"])
@login_required
def backup():
    user_id = session["user_id"]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"user_{user_id}_{stamp}"
    target.mkdir(parents=True, exist_ok=True)
    with get_db() as db:
        rows = db.execute("SELECT * FROM files WHERE user_id=? AND deleted=0", (user_id,)).fetchall()
    copied = 0
    import shutil
    for row in rows:
        source = UPLOAD_DIR / row["stored_name"]
        if source.exists():
            shutil.copy2(source, target / row["stored_name"])
            copied += 1
    flash(f"Backup created: {copied} file(s) copied to the local backups folder.", "success")
    return redirect(url_for("dashboard"))

@app.errorhandler(413)
def too_large(_error):
    flash("Upload request is too large.", "error")
    return redirect(url_for("dashboard"))

init_db()

if __name__ == "__main__":
    app.run(debug=True)
