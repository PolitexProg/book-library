# book-library (Goodreads Clone)

A lightweight Django-based book library and review app (Goodreads-inspired). This repository contains a small book-sharing social app with user accounts, profiles, friend requests, book entries, reviews, cover uploads, and simple social features.

This upgraded README adds clear setup, development, testing, and deployment instructions so contributors and reviewers can get the app running quickly.

## Features

- User registration, login, and profile management
- Profile pictures and book cover uploads (media handling)
- Book listings and detail pages
- Book reviews with timestamps
- Friend requests and friend list views
- Minimal, clean templates with static CSS

## Tech stack

- Python 3.11+ (use the Python version declared in `pyproject.toml` / your venv)
- Django (version pinned in `requirements.txt`)
- SQLite (default `db.sqlite3` for development)

## Quick start (development)

1. Clone the repo and create a virtual environment:

```bash
git clone https://github.com/PolitexProg/book-library.git
cd book-library
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (recommended) or edit `config/settings.py` for local use:

- `DJANGO_SECRET_KEY` - secret key for Django (for production always set this)
- `DJANGO_DEBUG` - `True` or `False` (default True for local dev)

You can export them in your shell for development:

```bash
export DJANGO_DEBUG=True
export DJANGO_SECRET_KEY='dev-secret-key'
```

4. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Collect static files (optional for development):

```bash
python manage.py collectstatic --noinput
```

6. Run the development server:

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Database & migrations

- This project uses SQLite by default (`db.sqlite3`). For production, configure `DATABASES` in `config/settings.py` to point to PostgreSQL or another DB.
- Migrations already exist in `app/migrations/` and `users/migrations/`. To add models or fields, create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Media and static files

- Uploaded book covers and profile pictures are stored under `media-files/` while development uses `MEDIA_ROOT` in settings.
- Static files are in `static/` and templates in `templates/`.

If you run into missing media during development, ensure `media-files/` directories exist and Django has write permissions:

```bash
mkdir -p media-files/book_covers media-files/profile_pics
```

## Tests

Run the Django test suite with:

```bash
python manage.py test
```

If tests fail because of local state (migrations or DB files), try removing `db.sqlite3` and running `migrate` again in a disposable dev environment.

## Common tasks

- Create a new app: `python manage.py startapp <appname>` and register in `config/settings.py`
- Make migrations: `python manage.py makemigrations` then `python manage.py migrate`
- Create a superuser: `python manage.py createsuperuser`

## Project structure (high level)

- `app/` — core book and review models, views, templates for books
- `users/` — custom user model, profiles, friend requests, auth views/templates
- `config/` — Django project settings, URLs, WSGI/ASGI
- `static/` — CSS and client static assets
- `media-files/` — uploaded content (book covers, profile pics)
- `db.sqlite3` — default local database file

## Deployment notes

- For production, set `DJANGO_DEBUG=False` and provide a secure `DJANGO_SECRET_KEY`.
- Use PostgreSQL (or managed DB) instead of SQLite for any production app with more than trivial usage.
- Serve static files via a CDN or web server (`collectstatic`) and configure `MEDIA_ROOT` and `MEDIA_URL` for media serving.
- Use gunicorn + Nginx or another WSGI/ASGI stack for deployment.

Example (Gunicorn + systemd) summary:

1. Install production dependencies and systemd unit for Gunicorn.
2. Set environment variables for SECRET_KEY and DB credentials.
3. `python manage.py collectstatic` and ensure `MEDIA_ROOT` served by Nginx.
4. Start gunicorn pointing to `config.wsgi:application`.

## Troubleshooting

- If file upload fails: ensure `MEDIA_ROOT` exists and is writable.
- If migrations conflict: inspect `app/migrations/` and `users/migrations/`, then reset local DB in development if safe.
- If static CSS isn't loaded: run `collectstatic` and check static URL paths in templates.

## Contributing

1. Fork the repo and create a feature branch `feature/your-change`.
2. Open a PR with a clear description of changes and testing steps.
3. Keep changes focused and include tests for new behavior where possible.

## License

See the repository `LICENSE` file.

## Contact

For questions or help, open an issue in the repository or contact the maintainer listed on GitHub.

---

If you want, I can also:

- Add a short CONTRIBUTING.md with development workflow and PR checklist.
- Add a small `run-dev.sh` helper script for setting up the venv, exporting common env vars, and running the server.

Tell me which of these you'd like next.
# Goodreads Clone

Minimal Goodreads-like Django app.

## Quickstart (development)

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create an env file from `.env.example` and fill values for `SECRET_KEY` and DB settings.

4. Run migrations and start server:

```bash
python manage.py migrate
python manage.py runserver
```

5. Run tests:

```bash
python manage.py test
```

## Publishing to GitHub

- Create a new repository on GitHub and push the project.
- GitHub Actions CI is included (`.github/workflows/ci.yml`) to run tests on pushes and PRs to `main`.

### Environment & secrets

- The project reads `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and DB settings from environment variables. For local development you can copy `.env.example` to `.env` and set values.
- On GitHub, add necessary repo secrets (e.g. `SECRET_KEY`, DB credentials) in repository Settings → Secrets when you set up CI.

## Notes
- Do not commit secrets. Use environment variables or GitHub repository secrets for CI.
- The project uses `MEDIA_ROOT` set to `media-files/`. Ensure this directory is in `.gitignore`.

## License
MIT
