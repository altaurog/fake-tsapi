import random
import numpy as np
import pytest
from api import data

@pytest.mark.parametrize('spec, expected', [
    ('temp', ['temp']),
])
def test_parse_spec(spec, expected):
    assert data.parse_spec(spec) == expected


@pytest.mark.parametrize('specs, expected', [
    ([["water", (2, 4)]],
     [["humidity", (2, 4)], ["dew", (2, 4)], ["precip", (2, 4)]]),
    ([["forecast"]], []),
])
def test_expand_tags(specs, expected):
    assert data.expand_tags(data.data_series, specs) == expected


@pytest.mark.parametrize('tag, ids', [
    ("feel", ["temp", "humidity", "winds"]),
    ("forecast", []),
])
def test_get_tag(tag, ids):
    assert data.get_tag(data.data_series, tag) == ids


@pytest.mark.parametrize('run', range(10))
def test_fake_data(run):
    lb = random.randrange(run, 49)
    ub = random.randrange(lb + 1, 100)
    assert lb < ub
    r = data.fake_data(500, lb, ub)
    assert r.min() < r.max()
    assert np.all(lb <= r)
    assert np.all(r <= ub)
