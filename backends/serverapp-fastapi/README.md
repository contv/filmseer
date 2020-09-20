# Server App

This is a server app for COMP9900 FilmFinder Project.

## Get Started

1. `poetry install`

2. Create a `.env` from `.env.template`

3. `poetry shell`

4. `uvicorn app.main:app --reload`

The `poetry run start` is buggy now and will be fixed soon.

## Test Pages

* The `/` should now be pointed to `~/public/index.html`.

* `/api/v1/` and `/api/v1/hello/world` works, these are two examples of routing.

## Development

VSCode Setup: `poetry run vscode_setup`

PyCharm has a poetry plugin so no need to worry about venv.
