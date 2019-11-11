from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from . import cities, data, util

router = APIRouter()

class ItemList(BaseModel):
    data: List[str]

class ErrorMessage(BaseModel):
    detail: str

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


@router.get("/location/{location}/data")
def get_data(
        location: str,
        start: datetime,
        end: datetime,
        period: str = Query(None, regex=r"\d+(i:[hdwmqy]|min)"),
        ids: str = None,
        tags: str = None,
    ):
    "Get series data for a location"
    if location not in cities.cities:
        raise HTTPException(status_code=404, detail="Location not found")
    specs = data.compile_query(ids or "", tags or "")
    scema = {**data.schema(specs), "location": location}
    return {"data": ["abcd", "efg"]}
