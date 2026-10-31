# CloudVault — Cloud-Based File Storage and Management System

A beginner-friendly academic prototype demonstrating cloud-storage concepts: user accounts, file upload/download, storage quotas, file search, trash/restore and local backup.

## Important project scope
This build runs locally and stores files on the computer running Flask. It is a **cloud-storage prototype**, not a production cloud service and not deployed to AWS/Azure/GCP. In your report and viva, describe it accurately as a local prototype demonstrating cloud-storage workflows.

## Requirements
- Python 3.10 or newer
- pip

## Run on Windows
1. Extract the ZIP.
2. Open the extracted folder in VS Code.
3. Open Terminal in that folder.
4. Run:

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

5. Open `http://127.0.0.1:5000` in your browser.
6. Create an account and sign in.

## Run on Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open `http://127.0.0.1:5000`.

## Free Render demo deployment

This repository includes `render.yaml` for a free Render web-service demo. The free service uses an ephemeral filesystem: uploaded files and the SQLite database may be lost when Render restarts, redeploys or spins the service down. Do not use it for important files or describe it as durable cloud storage.

1. Create a GitHub repository and push this project folder.
2. In Render, choose **New → Blueprint**, connect the GitHub repository, and apply the `render.yaml` configuration.
3. Open the generated `onrender.com` address and test with disposable files.

Vercel is not configured for this project. Its Python functions have a read-only filesystem apart from temporary `/tmp` storage, so the current SQLite and local-upload design would need to move to external database and object-storage services first.

## Demo steps for screenshots
1. Landing page (`01-home.png`)
2. Register a demo account (`02-register.png`)
3. Sign in and open dashboard (`03-dashboard.png`)
4. Upload a sample PDF or image (`04-uploaded-file.png`)
5. Move it to Trash and restore it (`05-trash-restore.png`)
6. Click Create backup (`06-backup.png`)

Capture screenshots from your own running application and place them in the `screenshots/` folder. Do not label mockups or sample images as real application screenshots.

## Main folders
- `app.py` — Flask routes, authentication, file management and backup logic
- `templates/` — HTML pages
- `static/css/` — interface styling
- `uploads/` — uploaded files
- `backups/` — local backup copies
- `cloud_storage.db` — SQLite database, created on first run

## Demo limitations and security notes
- Files are stored locally; there is no remote cloud object-storage provider connected.
- This is an educational prototype. Do not upload confidential or sensitive documents.
- Change `SECRET_KEY` before any non-local deployment.
- For production, add HTTPS, CSRF protection, malware scanning, rate limiting, cloud object storage, managed database, audit logs and robust backup/restore procedures.
