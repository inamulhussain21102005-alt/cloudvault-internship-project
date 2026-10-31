# INTERNSHIP PROJECT REPORT
## CLOUD-BASED FILE STORAGE AND MANAGEMENT SYSTEM

**Student Name:** [Your name]  
**Register Number:** [Your register number]  
**Department:** Computer Science and Engineering  
**College:** [College name]  
**Organization:** [Internship organization — fill only after confirmation]  
**Internship Period:** [Actual dates]  
**Project Guide:** [Guide name]

---

## Abstract
This project presents CloudVault, an academic prototype that demonstrates common file-storage workflows associated with cloud computing. The application provides user registration and authentication, file upload and download, file search, storage quota tracking, a trash-and-restore workflow, and local backup creation. Python Flask handles application routes, SQLite stores account and file metadata, and HTML, CSS and JavaScript provide the user interface. The current implementation runs on a local computer and uses local disk storage. It is intended to demonstrate cloud-storage concepts and is not represented as a production cloud deployment.

## 1. Introduction
Cloud computing provides on-demand access to computing resources such as storage, processing and applications over a network. Cloud storage allows users to store and retrieve digital files without managing the underlying storage hardware directly. This project models selected cloud-storage functions in a small web application.

## 2. Problem Statement
Managing digital files across folders can make it difficult to locate, organize, back up and recover information. The project aims to create a simple web-based interface for file management and demonstrate storage-related concepts such as user isolation, quota tracking and backup.

## 3. Objectives
- Build a simple web interface for file management.
- Provide account registration and sign-in.
- Allow users to upload and download supported files.
- Track each user's storage usage against a demonstration quota.
- Provide search, trash and restore operations.
- Demonstrate local backup creation.

## 4. Existing System and Proposed System
**Existing approach:** Users may manage files manually through local folders, making centralized access, search and recovery workflows less convenient.

**Proposed prototype:** A Flask web application provides a single interface for file upload, download, search, quota display, trash/restore and backup.

## 5. Technologies Used
- Python: application logic.
- Flask: web framework and routing.
- SQLite: relational database for users and file metadata.
- Werkzeug: password hashing and safe filename handling.
- HTML/CSS: page structure and styling.
- JavaScript: browser-side interactions where needed.

## 6. System Design
**Architecture:** Browser interface → Flask application → SQLite metadata database and local file-storage directory. The backup function copies active user files into a local backup directory.

**Main modules:** Authentication, upload validation, file listing/search, download, trash/restore, quota calculation and backup.

## 7. Implementation
Users first create an account and sign in. Passwords are stored as password hashes. After authentication, a user can upload supported files within the configured size and quota limits. Each file is assigned a unique stored filename while its original display name and metadata are recorded in SQLite. Downloads and file operations check ownership. Deleting a file marks it as deleted, allowing restoration from Trash. The backup feature copies active files into a timestamped local folder.

## 8. Testing
The following checks were run against the Flask application using its test client. They exercised the application routes and temporary test accounts; they did not use a real browser. The test records were removed after the checks.

| Test case | Expected result | Actual result |
|---|---|---|
| Register a new user | Account created | Passed |
| Sign in with correct details | Dashboard opens | Passed |
| Upload supported TXT file | File appears in the dashboard | Passed |
| View uploaded file | File name appears in the active file list | Passed |
| Download owned file | Original file content downloads | Passed |
| Delete active file | File leaves active list and appears in Trash | Passed |
| Restore trashed file | File returns to active list | Passed |
| Upload unsupported EXE file | Upload is rejected | Passed |
| Access another user's file | Request is denied | Passed with HTTP 404 |

## 9. Results and Screenshots
The route and file-operation checks above passed. Genuine browser screenshots still need to be captured from the application running on the student's Windows laptop and inserted here. Do not present generated mockups or test-client output as browser screenshots.

Recommended screenshots: home page; registration or login page with no password visible; dashboard; uploaded file in the list; download action; Trash; and the running terminal. Add the storage display and backup confirmation if those are included in the submission requirements.

## 10. Advantages
- Simple interface.
- Password hashing.
- Per-user file ownership checks.
- File type and size restrictions.
- Storage quota demonstration.
- Trash and restore workflow.
- Local backup demonstration.
- Uses free, open-source tools.

## 11. Limitations
The current version stores files on the local computer and is not accessible over the public internet by default. It does not use a cloud object-storage provider, distributed storage, cloud identity service or production-grade disaster recovery. The configured quota is a demonstration limit.

## 12. Future Enhancements
- Integrate an actual cloud object-storage service.
- Deploy the application on a cloud hosting platform.
- Add email verification and password reset.
- Add file sharing with permission controls.
- Add encryption at rest and audit logs.
- Add automated scheduled backups and monitoring.

## 13. Conclusion
CloudVault demonstrates the core workflow of a file-management application inspired by cloud-storage services. The project combines a Flask application, SQLite metadata storage and a browser-based interface to demonstrate authentication, file operations, quota tracking and backup. It provides a foundation for future integration with actual cloud infrastructure.

## References
- Flask documentation: https://flask.palletsprojects.com/
- Python documentation: https://docs.python.org/3/
- SQLite documentation: https://www.sqlite.org/docs.html
- Werkzeug documentation: https://werkzeug.palletsprojects.com/
