# COMP9900_FilmFinder
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg?style=flat-square)](https://github.com/prettier/prettier)

The FilmFinder Project for COMP9900-W17B-FilmSeer Group.

## How to run on VLAB
* This is a short version of how to run our project in VLAB. Please refer to the report for user manual

1. **Front-end initialization**
- Make sure .env file in `~/frontend/webapp-react` is configured correctly
- Go to `~/frontend/webapp-react` folder
- Run: `npm run build` followed by `npm run publish`
- Alternative, `npm run start` can be run for Developer mode

2. **Back-end initialization**
- Make sure .env file in `~/backend/serverapp-fastapi` is configured correctly
- Install poetry: https://python-poetry.org/docs/#installation
- Go to `~/backend/serverapp-fastapi`, run `poetry install`
- Run `poetry run start`
- Browse to http://localhost:xxxx (where xxxx is the configured port in `~/backend/serverapp-fastapi/.env`. The default value is 8000 in GitHub and 8123 in VLAB package


