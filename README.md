# COMP9900_FilmFinder
The FilmFinder Project for COMP9900-W17B-FilmSeer Group.

## Directory Structure

### `./`

The root directory of the project (similar to "solution" in Visual Studio). This root directory will be called `~/` below.

Please note that the `.gitignore` here should only contain project related and OS related items. Languages and library related items should be in the frontend / backend app directory.

### `~/frontend`

The main directory for frontend implementations. Docker configurations should also be stored here.

Please note that files should be compiled and moved to `~/public`. However, you should not modify `~/public` directly.

#### `~/frontend/webapp-react`

A web application frontend made with React. This is the root directory of the frontend project.

This application contains `npm run publish` to move files from `~/frontend/webapp-react/public` to `~/public`.

### `~/backend`

The main directory for backend implementations. Docker configurations should also be stored here.

#### `~/backend/serverapp-fastapi`

The backend in Python with FastAPI. This is the root directory of the backend project.

### `~/documents`

The proposal, report and other submissions may be stored here. Please note that this is not the generated API `docs` for our backend.

#### `~/documents/diaries`

The weekly diaries of each group member. Please create and only modify your own diary.

### `~/public`

This is the place where all the static assets should be stored. However, this is a **READ ONLY** directory for the backend: no user data and uploads should be stored here.

You should **never** create `api` directory in this folder: it will be ignored.

### `~/storages`

This is the place to store user data and posts (i.e. movies). The files inside this directory are generated and maintained by the backend. This directory can be stored as a separated mount for optimizations.

#### `~/storages/cache`

This is the place to store temporary cache. Nothing persistent should be stored here.

#### `~/storages/contents`

This is the place to store images and other user assets.

#### `~/storages/database`

The main database should be stored here. Please remember to keep the permission of this path minimal.

#### `~/storages/sessions`

This can be either a file based session storage, or a persistent storage of Redis if we use Redis.