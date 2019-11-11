from fastapi import FastAPI

from . import timeseries

app = FastAPI()
app.include_router(
    timeseries.router,
    prefix='/api/ts',
    tags=['series'],
)
