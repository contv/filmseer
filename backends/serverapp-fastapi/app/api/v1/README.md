## API v1

This is the root directory of API version 1. Common utilities and functions used in `routers` can be placed here so it won't be automatically imported.

### `routers`

All submodules inside this will be automatically imported to the router with a prefix of the cascaded module name. For example, `routers.hello.world` will be prefixed as `/api/v1/hello/world`.

Set `override_prefix` can customize the `world`, and `override_prefix_all` can customize `hello/world`. There is no way to override `/api/v1`, please set it in `.env`.

All assets under `/public` directory will be served statically, you may modify `app/core/static_router.py` to modify the rules of it. It might be a better choice to handle static files in Nginx, but it's also important that FastAPI can serve them as well.
