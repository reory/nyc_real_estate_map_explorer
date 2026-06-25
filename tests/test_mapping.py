import folium
from src.mapping import get_hex_color, generate_full_map
from hypothesis import given, strategies as st


def test_get_hex_color_low_price():

    assert get_hex_color(30000) == "#2ecc71"


def test_get_hex_color_mid_price():

    assert get_hex_color(600000) == "#e67e22"


def test_get_hex_color_high_price():

    assert get_hex_color(2000000) == "#e74c3c"


def test_get_hex_color_none():

    assert get_hex_color(None) == "#7f8c8d"


def test_generate_full_map_returns_folium_map():

    props = [
        {"latitude": 40.7, "longitude": -74.0, "price": 500000},
        {"latitude": 40.8, "longitude": -73.9, "price": 900000},
    ]
    map = generate_full_map(props)
    assert isinstance(map, folium.Map)


@given(st.one_of(st.none(), st.integers(), st.floats(allow_nan=False)))
def test_get_hex_color_property_based(price):
    color = get_hex_color(price)
    assert isinstance(color, str)
    assert color.startswith("#")
    assert len(color) == 7
