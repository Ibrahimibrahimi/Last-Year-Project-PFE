# Flask User Authentication App

A lightweight web application built with **Flask** that provides user registration, login, logout, and user listing functionality. Uses **SQLAlchemy** for ORM-based database management, **Flask-Login** for session handling, and **Werkzeug** for secure password hashing.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Database Schema](#database-schema)
- [API Routes & Endpoints](#api-routes--endpoints)
- [Templates](#templates)
- [Static Assets](#static-assets)
- [Configuration & Environment Variables](#configuration--environment-variables)
- [Logging](#logging)
- [Known Issues & Developer Notes](#known-issues--developer-notes)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)

---

## Overview

This project is a Flask-based user authentication system. It supports:
- Creating new user accounts with hashed passwords
- Logging in and out with session management
- Viewing all registered users
- Persistent storage via a SQLite database (with PostgreSQL support via `psycopg2-binary`)
- Rotating file-based application logging

The application follows the **Application Factory** pattern using `createApp()` and is structured around Flask **Blueprints** for modular routing.

---

## Project Structure

```
project/
├── run.py                          # Entry point — creates the app and starts the server
├── .env                            # Environment variables (database URL, secrets)
├── requirements.txt                # Python dependencies
├── activate venv.bat               # Windows batch script to activate virtual environment
│
├── instance/
│   └── mydatabase.db               # SQLite database file (auto-created on first run)
│
├── docs/
│   ├── problems.txt                # Developer notes on encountered bugs and their solutions
│   └── remember.txt                # Developer reminders and configuration tips
│
└── app/
    ├── __init__.py                 # Application factory (createApp), blueprint registration, logging setup
    ├── models.py                   # SQLAlchemy ORM model: User
    ├── extensions.py               # Flask extensions: db, migrate, login_manager
    │
    ├── auth/
    │   ├── __init__.py             # Auth blueprint definition
    │   └── routes.py               # Routes: /login, /register, /logout
    │
    ├── main/
    │   ├── __init__.py             # Main blueprint definition
    │   └── routes.py               # Routes: / (home), /users
    │
    ├── templates/
    │   ├── base.html               # Base HTML template (CSS, viewport meta, block structure)
    │   ├── login.html              # Login form — extends base.html
    │   ├── register.html           # Registration form (standalone, not yet extending base)
    │   └── users.html              # Displays all registered users
    │
    ├── static/
    │   ├── css/
    │   │   └── main.css            # Global stylesheet
    │   ├── js/
    │   │   └── main.js             # Frontend JavaScript (currently empty)
    │   └── uploads/                # Directory reserved for user-uploaded files
    │
    └── logs/
        └── main.log                # Rotating application log file
```

---

## Tech Stack

| Layer            | Technology                          | Version   |
|------------------|--------------------------------------|-----------|
| Web Framework    | Flask                                | 3.1.3     |
| ORM              | Flask-SQLAlchemy / SQLAlchemy        | 3.1.1 / 2.0.46 |
| DB Migrations    | Flask-Migrate (Alembic)              | 4.1.0     |
| Authentication   | Flask-Login                          | 0.6.3     |
| Password Hashing | Werkzeug                             | 3.1.6     |
| Templating       | Jinja2                               | 3.1.6     |
| Database         | SQLite (default) / PostgreSQL        | —         |
| Env Management   | python-dotenv                        | 1.2.1     |
| Python Version   | CPython                              | 3.10      |

---

## Features

- **User Registration** — Collects username, email, password, date of birth, and bio. Passwords are stored as Werkzeug-generated hashes. Duplicate email addresses are rejected with a user-facing error message.
- **User Login** — Validates credentials against the database. Displays specific error messages for unrecognised emails and incorrect passwords.
- **User Logout** — Ends the user session and redirects to the login page. Requires the user to be authenticated.
- **User Listing** — A public endpoint (`/users`) that renders all registered users from the database. Displays a call-to-action if no users exist yet.
- **Protected Home Route** — The `/` route requires authentication via `@login_required`. Unauthenticated requests are redirected to `/login`.
- **Application Logging** — Server events and user creation actions are written to a rotating log file (`app/logs/main.log`, max 10 KB, 5 backups).

---

## Database Schema

### Table: `user`

| Column     | Type          | Constraints                          | Default              |
|------------|---------------|--------------------------------------|----------------------|
| `id`       | Integer       | Primary Key, Auto-increment          | —                    |
| `email`    | String(30)    | Unique, Not Null                     | —                    |
| `password` | String(300)   | Not Null                             | — *(stored as hash)* |
| `username` | String(30)    | Not Null                             | —                    |
| `birth`    | Date          | —                                    | `2006-04-10`         |
| `bio`      | String(100)   | —                                    | `"Hi i'm learning"`  |

> **Note:** The `User` model does not yet implement `UserMixin` from Flask-Login, which is required for session management to work correctly. See [Known Issues](#known-issues--developer-notes).

---

## API Routes & Endpoints

### Auth Blueprint (`/`)

| Method     | Endpoint     | Auth Required | Description                                                                 |
|------------|--------------|---------------|-----------------------------------------------------------------------------|
| GET        | `/login`     | No            | Renders the login form                                                       |
| POST       | `/login`     | No            | Authenticates user by email and password; logs in on success                |
| GET        | `/register`  | No            | Renders the registration form                                                |
| POST       | `/register`  | No            | Creates a new user; returns error if email already exists                   |
| GET        | `/logout`    | Yes           | Logs out the current user; redirects to login                               |

### Main Blueprint (`/`)

| Method | Endpoint  | Auth Required | Description                                            |
|--------|-----------|---------------|--------------------------------------------------------|
| GET    | `/`       | Yes           | Home route — currently returns a plain string `"HOME"` |
| GET    | `/users`  | No            | Renders a list of all registered users                  |

---

## Templates

| Template          | Extends      | Description                                                                                          |
|-------------------|--------------|------------------------------------------------------------------------------------------------------|
| `base.html`       | —            | Base layout; links `main.css`, defines `pagetitle` and `pagebody` Jinja2 blocks. *(Note: CSS URL has a bug — see Known Issues.)* |
| `login.html`      | `base.html`  | Login form with inline validation error display for email and password fields. Shows success message after registration. |
| `register.html`   | *(none)*     | Standalone registration form collecting username, email, password, birth date, and bio. Does not yet extend `base.html`. |
| `users.html`      | *(none)*     | Iterates over all `User` objects and displays username and password hash. Shows a registration/login prompt if no users exist. |

---

## Static Assets

| File                     | Description                                                       |
|--------------------------|-------------------------------------------------------------------|
| `static/css/main.css`    | Global stylesheet. Currently sets `body { color: red; }`.        |
| `static/js/main.js`      | Frontend JavaScript file. Currently empty — reserved for future use. |
| `static/uploads/`        | Empty directory reserved for future file upload functionality.    |

---

## Configuration & Environment Variables

The application reads configuration from a `.env` file in the project root using `python-dotenv`.

| Variable      | Description                                                                             | Example Value                    |
|---------------|-----------------------------------------------------------------------------------------|----------------------------------|
| `databaseURL` | SQLAlchemy-compatible database connection string. Use a relative path for SQLite.       | `sqlite:///mydatabase.db`        |

> The `SECRET_KEY` is generated at runtime using `os.urandom(16)`. This means sessions are invalidated every time the server restarts. For production, this should be set to a fixed value stored in `.env`.

**Sample `.env` file:**
```env
databaseURL=sqlite:///mydatabase.db
```

> For PostgreSQL, use:
> ```env
> databaseURL=postgresql://user:password@localhost:5432/dbname
> ```

---

## Logging

The application uses Python's `logging` module with a `RotatingFileHandler`.

| Setting      | Value                      |
|--------------|----------------------------|
| Log file     | `app/logs/main.log`        |
| Max file size | 10,240 bytes (10 KB)      |
| Backup count | 5                          |
| Log level    | `INFO`                     |
| Format       | `%(asctime)s - %(levelname)s - %(message)s` |

**Events that are logged:**
- Server startup: `SERVER STARTED SUCCESSFULLY`
- New user registration: `User created successfully email=<email>`

---

## Known Issues & Developer Notes

The following are documented issues noted during development (sourced from `docs/problems.txt` and `docs/remember.txt`):

### 1. `render_template()` not working — Missing `user_loader` or `request_loader`
- **Problem:** Encountered when `render_template()` failed due to Flask-Login not being properly initialised.
- **Root cause:** The issue originated from `flask-login` requiring some initialisation steps.
- **Solution:** Ensure `user_loader` is defined and that all required extensions are properly set up in `extensions.py` and initialised in `createApp()`.

### 2. `no such column: users.email`
- **Problem:** SQLAlchemy could not find the `email` column on the `users` table.
- **Root cause:** Flask-Migrate was not used — the database schema was out of sync with the model.
- **Solution:**
  1. Delete the existing database file and recreate it, **or**
  2. Use Flask-Migrate properly (`flask db init` → `flask db migrate` → `flask db upgrade`)

### 3. Database URL configuration reminder
- The `databaseURL` value in `.env` must use **3 slashes** for a relative SQLite path:
  - `sqlite:///` → relative path (recommended for development)
  - `sqlite:////` → absolute path

### 4. `SECRET_KEY` is ephemeral
- Currently generated with `os.urandom(16)` on every app start.
- This invalidates all active sessions on server restart.
- **Recommended fix:** Store a fixed key in `.env` and load it via `os.getenv("SECRET_KEY")`.

### 5. `login()` route — inverted password check logic
- In `auth/routes.py`, the condition `if check_password_hash(user.password, password)` returns `True` when passwords **match**, but the current code treats this as a failure.
- The correct logic should be: `if not check_password_hash(user.password, password)` → show "Wrong password" error.

### 6. `User` model missing `UserMixin`
- Flask-Login requires the `User` model to implement `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()`.
- The easiest fix is to inherit from `flask_login.UserMixin`: `class User(db.Model, UserMixin)`.

### 7. CSS path bug in `base.html`
- The static CSS URL is rendered as:
  ```html
  <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}.css">
  ```
  The `.css` extension is appended twice, resulting in a broken path. Remove the trailing `.css`.

---

## Installation & Setup

### Prerequisites
- Python 3.10+
- `pip`
- (Optional) `virtualenv` or `venv`

### Steps

**1. Clone or extract the project:**
```bash
cd project/
```

**2. Create and activate a virtual environment:**

On Windows:
```bash
activate venv.bat
```

On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables:**

Create a `.env` file in the project root:
```env
databaseURL=sqlite:///mydatabase.db
```

---

## Running the Application

```bash
python run.py
```

The server will start at:
```
http://0.0.0.0:8080
```

On first run, `db.create_all()` is called automatically to create the database tables based on the defined models.

**Available pages:**

| URL          | Description                     |
|--------------|---------------------------------|
| `/login`     | User login page                 |
| `/register`  | New account registration page   |
| `/users`     | List of all registered users    |
| `/`          | Protected home page             |
| `/logout`    | Logs out the current user       |
