# voyager-backend
A backend and API service for serving the Voyager application. 

It is a FastAPI that can be run with `gunicorn` in production. A data directory, where voyage data in the correct format can be found, needs to be provided in the config file.
Instead of `gunicorn`, the app can also be run locally with `fastapi run` if the cli-package `fastapi[standard]` is installed additionally.

The voyager base module is currently found in [another repository](https://github.com/waahlstrand/voyager/tree/main) and needs revision.
