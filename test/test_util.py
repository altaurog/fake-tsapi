import pytest
from api import cities, util

@pytest.mark.parametrize("pattern, expected", [
    ('SA', [
        "busan",
        "kinshasa",
        "osaka",
        "san-francisco",
        "san-jose",
        "santiago",
        "sao-paulo",
    ]),
    ('d?l', [
        "dallas",
        "delhi",
        "guadalajara",
        "philadelphia",
    ]),
    ('n*ch', [
        "munich",
        "nanchang",
    ]),
])
def test_search(pattern, expected):
    assert list(util.search(cities.cities, pattern)) == expected
