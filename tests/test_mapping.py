import folium
from hypothesis import given
from hypothesis import strategies as st

from src.mapping import generate_full_map, get_hex_color


def test_get_hex_color_low_price():
    """Verify low-priced properties use the green color scale."""

    assert get_hex_color(30000) == "#2ecc71"


def test_get_hex_color_mid_price():
    """Verify mid-priced properties use the orange color scale."""

    assert get_hex_color(600000) == "#e67e22"


def test_get_hex_color_high_price():
    """Verify high-priced properties use the red color scale."""

    assert get_hex_color(2000000) == "#e74c3c"


def test_get_hex_color_none():
    """Verify missing prices return the default color."""

    assert get_hex_color(None) == "#7f8c8d"


def test_generate_full_map_returns_folium_map():
    """Verify map generation returns a Folium map object."""

    props = [
        {"latitude": 40.7, "longitude": -74.0, "price": 500000},
        {"latitude": 40.8, "longitude": -73.9, "price": 900000},
    ]
    map = generate_full_map(props)
    assert isinstance(map, folium.Map)


@given(st.one_of(st.none(), st.integers(), st.floats(allow_nan=False)))
def test_get_hex_color_property_based(price):
    """Property-based test for valid hex color generation."""

    color = get_hex_color(price)
    assert isinstance(color, str)
    assert color.startswith("#")
    assert len(color) == 7
