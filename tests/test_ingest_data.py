import pandas as pd
import src.ingest_data as ingest_data


def test_ingest_adds_valid_properties(monkeypatch):

    # Fake ZIP coordinate CSV
    zips_df = pd.DataFrame(
        {
            "zip": ["10001"],
            "lat": [40.75],
            "lng": [-73.99],
        }
    )

    # Fake NY properties CSV
    props_df = pd.DataFrame(
        {
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
        }
    )

    # Patch pandas.read_csv
    def fake_read_csv(path, dtype=None):
        if "uszips" in path:
            return zips_df
        return props_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    # Capture calls to session.add() and commit()
    added = []
    committed = []

    class DummySession:
        def add(self, obj):

            added.append(obj)

        def commit(self):

            committed.append(True)

    dummy_session = DummySession()

    # Patch BOTH Session() AND the module-level session
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

    # ZIP CSV with missing lat/lng
    zips_df = pd.DataFrame(
        {
            "zip": ["10001"],
            "lat": [None],
            "lng": [None],
        }
    )

    # NY properties CSV
    props_df = pd.DataFrame(
        {
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
        }
    )

    def fake_read_csv(path, dtype=None):

        if "uszips" in path:
            return zips_df
        return props_df

    monkeypatch.setattr(pd, "read_csv", fake_read_csv)

    added = []

    class DummySession:
        def add(self, obj):
            added.append(obj)

        def commit(self):
            pass

    monkeypatch.setattr(ingest_data, "Session", lambda: DummySession())

    ingest_data.ingest()

    # No properties should be added because coordinates are missing
    assert len(added) == 0
