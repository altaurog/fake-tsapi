"""
dummy data backend
"""
from itertools import chain
from functools import partial, reduce
from typing import Dict, List, Set

import numpy as np
import pandas as pd
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
        "missingValues": [""],
        "notFound": not_found,
        "series": {f["series"]: data_series.get(f["series"], {}) for f in found},
    }

def field(spec: list) -> dict:
    series = data_series.get(spec[0])
    if not series:
        return {}
    return {
        "name": "".join(map(str, spec)),
        "type": "number",
        "series": spec[0],
    }

def get_data(series: Dict[str, dict], start: float, end: float):
    data = partial(get_series, start=start, end=end)
    return pd.DataFrame({s: data(d) for s, d in series.items()})

def get_series(s: dict, start: float, end: float):
    t = pd.to_datetime(np.round(timestamps(start, end)), unit='s')
    d = fake_data(len(t), *s["range"])
    return pd.Series(d, index=t)

def timestamps(start: float, end: float):
    count = int(end - start) // 120  # samples every two minutes on average
    s, e = random(2) * 120
    return to_range(random(count - 1).cumsum(), start + s, end - e)

def fake_data(count: int, lower_bound: float, upper_bound: float):
    drange = upper_bound - lower_bound
    lb, ub = np.sort(random(2) * drange + lower_bound)
    return to_range((random(count) - 0.5).cumsum(), lb, ub)

def to_range(data, lb, ub):
    dmin, dmax = data.min(), data.max()
    return (data - dmin) * (ub - lb) / (dmax - dmin) + lb

data_series: dict = {
    "temp": {
        "description": "Temperature",
        "unit": "°C",
        "range": (-4, 44),
        "tags": ["feel"],
    },
    "pressure": {
        "description": "Atmospheric Pressure",
        "range": (995, 1018),
        "unit": "hPa",
    },
    "humidity": {
        "description": "Relative Humidity",
        "unit": "%",
        "range": (0, 90),
        "tags": ["feel", "water"],
    },
    "dew": {
        "description": "Dew Point",
        "unit": "°C",
        "range": (1, 14),
        "tags": ["water"],
    },
    "winds": {
        "description": "Wind Speed",
        "unit": "km/h",
        "range": (0, 50),
        "tags": ["feel"],
    },
    "windd": {
        "description": "Wind Direction",
        "unit": "°",
        "range": (0, 360),
    },
    "precip": {
        "description": "Precipitation",
        "unit": "mm",
        "range": (0, 30),
        "tags": ["water"],
    },
    "part": {
        "description": "Particulate Matter",
        "unit": "µg/m3",
        "range": (0, 100),
        "tags": ["quality"],
    },
}
