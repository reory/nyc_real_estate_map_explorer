# Mock SQLAlchemy so don’t need a real DB connection.abs

from src.database import get_filtered_properties


class DummyProp:
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

    dummy_data = [DummyProp(500000), DummyProp(700000)]

    class DummyQuery:
        def filter(self, *args, **kwargs):
            return self

        def limit(self, n):
            return self

        def all(self):
            return dummy_data

    class DummySession:
        def query(self, *args, **kwargs):
            return DummyQuery()

        def close(self):
            pass

    monkeypatch.setattr("src.database.Session", lambda: DummySession())

    results = get_filtered_properties(100000, 800000)
    assert len(results) == 2
    assert isinstance(results[0], dict)
    assert "price" in results[0]
