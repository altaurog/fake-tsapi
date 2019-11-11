"""
dummy data backend
"""
from itertools import chain
from functools import reduce
from typing import List, Set

import numpy as np
random = np.random.random   # pylint: disable=no-member

def get_tags() -> Set[str]:
    tags_iter = (s.get("tags", []) for s in data_series.values())
    return set(chain.from_iterable(tags_iter))

def compile_query(idstr: str, tagstr: str):
    f = lambda s: map(parse_spec, s.replace(' ', '').split(','))
    return list(f(idstr)) + expand_tags(data_series, list(f(tagstr)))

def parse_spec(qstr: str) -> list:
    return [qstr]

def expand_tags(series: dict, specs: List[list]) -> List[list]:
    def tag_reduce(agg, spec):
        [tag, *rs] = spec
        return agg + [[s, *rs] for s in get_tag(series, tag)]
    return reduce(tag_reduce, specs, [])

def get_tag(series: dict, tag: str) -> List[str]:
    return [s for s, d in series.items() if tag in d.get("tags", [])]

def schema(specs: List[list]) -> dict:
    found = list(filter(None, map(field, specs)))
    not_found = [s[0] for s in specs if s[0] not in data_series]
    return {
        "fields": found,
        "missingValues": not_found,
        "series": {f["series"]: data_series.get(f["series"], {}) for f in found},
    }

def field(spec: list) -> dict:
    series = data_series.get(spec[0])
    if not series:
        return {}
    return {
        "name": "".join(map(str, spec)),
        "type": series["type"],
        "series": spec[0],
    }

def fake_data(count: int, lower_bound: float, upper_bound: float):
    drange = upper_bound - lower_bound
    lb, ub = np.sort(random(2) * drange + lower_bound)
    rand = (random(count) - 0.5).cumsum()
    rrange = rand.max() - rand.min()
    return (rand - rand.min()) * (ub - lb) / rrange + lb

data_series: dict = {
    "temp": {
        "description": "Temperature",
        "type": "number",
        "unit": "°C",
        "range": (-4, 44),
        "tags": ["feel"],
    },
    "pressure": {
        "description": "Atmospheric Pressure",
        "type": "number",
        "range": (995, 1018),
        "unit": "hPa",
    },
    "humidity": {
        "description": "Relative Humidity",
        "type": "number",
        "unit": "%",
        "range": (0, 90),
        "tags": ["feel", "water"],
    },
    "dew": {
        "description": "Dew Point",
        "type": "number",
        "unit": "°C",
        "range": (1, 14),
        "tags": ["water"],
    },
    "winds": {
        "description": "Wind Speed",
        "type": "number",
        "unit": "km/h",
        "range": (0, 50),
        "tags": ["feel"],
    },
    "windd": {
        "description": "Wind Direction",
        "type": "number",
        "unit": "°",
        "range": (0, 360),
    },
    "precip": {
        "description": "Precipitation",
        "type": "number",
        "unit": "mm",
        "range": (0, 30),
        "tags": ["water"],
    },
    "part": {
        "description": "Particulate Matter",
        "type": "number",
        "unit": "µg/m3",
        "range": (0, 100),
        "tags": ["quality"],
    },
}
