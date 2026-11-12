import pandas as pd

from src import ingest_data


def test_ingest_adds_valid_properties(monkeypatch):
    """Verify valid property records are ingested and committed."""

    # A single mock DataFrame simulating "data/nyc_properties_clean.csv" 
    # which already has lat/lng coordinates merged in.
    mock_merged_df = pd.DataFrame({
        "zip_code": ["10001"],
        "status": ["for_sale"],
        "price": [500000],
        "bed": [2],
        "bath": [1],
        "acre_lot": [0.1],
        "city": ["NYC"],
        "state": ["New York"],
        "house_size": [900],
        "prev_sold_date": ["2020-01-01"],
        "lat": [40.75],
        "lng": [-73.99],
    })

    # Since ingest() only reads one CSV, return the complete DataFrame
    def fake_read_csv(path, *args, **kwargs):
        """Return mock property data for ingestion tests."""

        return mock_merged_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    # Capture calls to session.add() and commit()
    added = []
    committed = []

    class DummySession:
        """Mock database session for ingestion testing."""

        def add(self, obj):
            """Capture added property records."""

            added.append(obj)

        def commit(self):
            """Track database commit operations."""

            committed.append(True)

    dummy_session = DummySession()

    # Patch both Session and the active module session reference
    monkeypatch.setattr(ingest_data, "Session", lambda: dummy_session)
    monkeypatch.setattr(ingest_data, "session", dummy_session)

    # Run ingestion
    ingest_data.ingest()

    # Assertions
    assert len(added) == 1
    assert len(committed) >= 1

    prop = added[0]
    assert prop.price == 500000
    assert prop.city == "NYC"
    assert prop.latitude == 40.75
    assert prop.longitude == -73.99


def test_ingest_skips_missing_coordinates(monkeypatch):
    """Verify properties without coordinates are skipped."""

    # Mock DataFrame where coordinate information is missing/NaN
    mock_corrupted_df = pd.DataFrame({
        "zip_code": ["10001"],
        "status": ["for_sale"],
        "price": [500000],
        "bed": [2],
        "bath": [1],
        "acre_lot": [0.1],
        "city": ["NYC"],
        "state": ["New York"],
        "house_size": [900],
        "prev_sold_date": ["2020-01-01"],
        "lat": [None],
        "lng": [None],
    })

    def fake_read_csv(path, *args, **kwargs):
        """Return property data with missing coordinates."""

        return mock_corrupted_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    added = []

    class DummySession:
        """Mock database session for ingestion testing."""

        def add(self, obj):
            """Capture added property records."""

            added.append(obj)

        def commit(self):
            """Mock database commit operation."""


    dummy_session = DummySession()
    monkeypatch.setattr(ingest_data, "Session", lambda: dummy_session)
    monkeypatch.setattr(ingest_data, "session", dummy_session)

    ingest_data.ingest()

    # No properties should be added because coordinates are missing
    assert len(added) == 0
