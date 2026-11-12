# Mock SQLAlchemy so don’t need a real DB connection.abs

from src.database import get_filtered_properties


class DummyProp:
    """Mock NYC property used in tests."""

    def __init__(self, price):
        self.price = price
        self.latitude = 40.7
        self.longitude = -74.0
        self.bed = 2
        self.bath = 1
        self.house_size = 900
        self.acre_lot = 0.1
        self.city = "NYC"
        self.county_name = "New York"


def test_filtered_properties_returns_clean_dicts(monkeypatch):
    """Verify property records are returned as clean dictionaries."""

    dummy_data = [DummyProp(500000), DummyProp(700000)]

    class DummyQuery:
        """Mock query object returning test property data."""

        def filter(self, *args, **kwargs):
            """Mock query filtering."""

            return self

        def limit(self, n):
            """Mock result limiting."""

            return self

        def all(self):
            """Return mock property records."""

            return dummy_data

    class DummySession:
        """Mock database session for testing queries."""

        def query(self, *args, **kwargs):
            """Return a mock query object."""

            return DummyQuery()

        def close(self):
            """No-op session close."""


    monkeypatch.setattr("src.database.Session", lambda: DummySession())

    results = get_filtered_properties(100000, 800000)
    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert "price" in results[0]
