import pandas as pd
import plotly.graph_objects as go

from src import analytics


def test_clean_borough_name_by_county():
    """Ensure county names are correctly mapped to their respective NYC boroughs."""

    # Test county matching rule
    assert analytics.clean_borough_name({"county_name": "Kings County", "city": "Unknown"}) == "Brooklyn"
    assert analytics.clean_borough_name({"county_name": "Queens County", "city": "Unknown"}) == "Queens"
    assert analytics.clean_borough_name({"county_name": "New York County", "city": "Unknown"}) == "Manhattan"
    assert analytics.clean_borough_name({"county_name": "Bronx County", "city": "Unknown"}) == "Bronx"
    assert analytics.clean_borough_name({"county_name": "Richmond County", "city": "Unknown"}) == "Richmond"


def test_clean_borough_name_by_neighborhood_map():
    """Verify neighborhood lookup dictionary correctly categorises known NYC localities."""

    # Test dictionary map lookup
    assert analytics.clean_borough_name({"county_name": "", "city": "Bed Stuy"}) == "Brooklyn"
    assert analytics.clean_borough_name({"county_name": "", "city": "Astoria"}) == "Queens"
    assert analytics.clean_borough_name({"county_name": "", "city": "Manhattan"}) == "Manhattan"
    assert analytics.clean_borough_name({"county_name": "", "city": "Riverdale"}) == "Bronx"
    assert analytics.clean_borough_name({"county_name": "", "city": "Staten Island"}) == "Richmond"


def test_clean_borough_name_by_fallback_substring():
    """Check substring fallback matching for partially specified neighborhood names."""

    # Test substring matching fallback
    assert analytics.clean_borough_name({"county_name": "", "city": "Some Brooklyn Area"}) == "Brooklyn"
    assert analytics.clean_borough_name({"county_name": "", "city": "North Queens"}) == "Queens"
    assert analytics.clean_borough_name({"county_name": "", "city": "Downtown New York"}) == "Manhattan"
    assert analytics.clean_borough_name({"county_name": "", "city": "East Bronx"}) == "Bronx"
    assert analytics.clean_borough_name({"county_name": "", "city": "Staten Island North"}) == "Richmond"


def test_clean_borough_name_outside_and_other_nyc():
    """Validate classification of non-NYC regions versus unrecognised local entries."""

    # Test outside NYC vs Other NYC
    assert analytics.clean_borough_name({"county_name": "", "city": "White Plains"}) == "Outside NYC"
    assert analytics.clean_borough_name({"county_name": "", "city": "Unknown Neighborhood"}) == "Other NYC"


def test_generate_borough_price_box():
    """Verify plotly box plot generation for borough price distributions."""

    df = pd.DataFrame({
        "city": ["Astoria", "Bed Stuy", "White Plains"],
        "county_name": ["Queens", "Kings", "Westchester"],
        "price": [500000, 750000, 1000000],
        "house_size": [1000, 1200, 1500]
    })
    fig = analytics.generate_borough_price_box(df)
    assert isinstance(fig, go.Figure)


def test_generate_size_vs_price_scatter():
    """Verify plotly scatter plot generation for house size versus price."""

    df = pd.DataFrame({
        "city": ["Astoria", "Bed Stuy"],
        "county_name": ["Queens", "Kings"],
        "price": [500000, 750000],
        "house_size": [1000, 1200]
    })
    fig = analytics.generate_size_vs_price_scatter(df)
    assert isinstance(fig, go.Figure)