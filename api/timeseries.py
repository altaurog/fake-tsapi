from datetime import datetime
import io
import json
from typing import Dict, List
from fastapi import APIRouter, HTTPException, Query
from matplotlib import pyplot as plt
import pandas as pd
from pydantic import BaseModel
from starlette.responses import Response

from . import cities, data, util

router = APIRouter()

class ItemList(BaseModel):
    data: List[str]

class ErrorMessage(BaseModel):
    detail: str

class CSVResponse(Response):
    media_type = "text/csv"

responses = {
    "responses": {
        404: {"model": ErrorMessage, "description": "The item was not found"},
    }
}

@router.get("/locations", response_model=ItemList)
def list_locations(q: str = None):
    "List locations for which data is available"
    found = util.search(cities.cities, q)
    return {"data": list(found)}

@router.get("/location/{location}/ids", response_model=ItemList, **responses)
def list_ids(location: str, q: str = None):
    "List series ids for a location"
    if location not in cities.cities:
        raise HTTPException(status_code=404, detail="Location not found")
    found = util.search(data.data_series, q)
    return {"data": list(found)}

@router.get("/location/{location}/tags", response_model=ItemList, **responses)
def list_tags(location: str, q: str = None):
    "List series tags for a location"
    if location not in cities.cities:
        raise HTTPException(status_code=404, detail="Location not found")
    found = util.search(data.get_tags(), q)
    return {"data": list(found)}


@router.get("/location/{location}/data",
    response_class=CSVResponse,
    responses={
        200: {"content": {
            "application/json": {},
            "text/html": {},
            "text/plain": {},
            "image/png": {},
        }},
        400: {"model": ErrorMessage, "description": "Illegal parameters"},
        406: {"model": ErrorMessage, "description": "Unrecognized format"},
    },
)
def get_data(
        location: str,
        start: datetime,
        end: datetime,
        period: str = Query(None, regex=r"^\d+(?i:[shdwmqy]|min)$"),
        ids: str = None,
        tags: str = None,
        format: str = 'csv',
    ):
    """
    Get series data for a location

    [Frictionless data](https://frictionlessdata.io/specs/table-schema/)
    schema is included in `Content-Schema` response header.

    ## query parameters:

    **start**:
        timestamp in ISO 8601 format: `2019-10-12T21:07:00+03:00`

    **end**:
        timestamp in ISO 8601 format.

    **period**:
        aggregation period length.
        Must be an integer followed by a unit: `30min`
        (see units below).

    **ids**:
        comma-separated list of series ids to query,
        with optional aggregation (see below).

    **tags**:
        comma-separated list of series tags,
        with optional aggregation (see below).

    **format**:
        response format.
        One of `csv` (default), `json`, `html`, `text`, `png`

    ## aggregation:

    Aggregation is specified as a qualifier on ids and tags: `temp.mean`

    Available aggregations are:
    `count`, `max`, `min`, `mean`, `std`, `sum`.

    ### period units:

        === =======
        s   second
        min minute
        h   hour
        d   day
        w   week
        m   month
        q   quarter
        y   year
        === =======
    """
    if location not in cities.cities:
        raise HTTPException(status_code=404, detail="Location not found")
    specs = data.compile_query(ids or "", tags or "")
    freqstr = data.validate(specs, period)
    schema = {**data.schema(specs), "location": location}
    df = data.get_data(schema["series"], start.timestamp(), end.timestamp())
    pdf = data.process_data(df, freqstr, specs)
    headers = {'Content-Schema': json.dumps(schema)}
    return response(format, pdf, headers)

def response(fmt: str, df: pd.DataFrame, headers: Dict[str, str]) -> Response:
    if fmt == "csv":
        res = df.to_csv(float_format="%0.3f")
        return Response(content=res, headers=headers)
    if fmt == "json":
        res = df.reset_index(
            ).to_json(orient="records", date_format="iso", double_precision=3)
        return Response(content=res, headers=headers, media_type="application/json")
    if fmt == "html":
        res = df.to_html(na_rep="", float_format="%0.3f")
        return Response(content=res, headers=headers, media_type="text/html")
    if fmt == "text":
        res = df.to_string(na_rep="", float_format="%0.3f")
        return Response(content=res, headers=headers, media_type="text/plain")
    if fmt == "png":
        plt.figure()
        df.plot()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        return Response(content=buf.getvalue(), headers=headers, media_type="image/png")
    raise HTTPException(status_code=406, detail="Unrecognized format: " + fmt)
