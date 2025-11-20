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
