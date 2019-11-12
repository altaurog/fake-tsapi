timeseries api
==============

A fake REST timeseries api, as an excuse to play with FastAPI

Features
---------

* openapi documentation
* ReDoc (``/redoc``) and Swagger UI (``/docs``)
* multiple response formats
* query by series id or tag
* multiple series
* time range
* aggregations (with period specified)
* frictionless schema response header

TODO
----
* thresholds
* query multiple locations

Running
-------

Run server with ``uvicorn api.app:app``

Run tests with ``pytest test``
