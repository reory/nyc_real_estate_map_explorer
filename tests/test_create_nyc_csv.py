# Mock pandas so no real CSV files are touched.

import pandas as pd
from src.create_nyc_csv import create_ny_only_csv


def test_create_nyc_only_csv(monkeypatch):
    saved = {}

    # Dynamically return mock data based on the file type being read
    def fake_read_csv(path, *args, **kwargs):
        if "zips" in str(path) or "uszips" in str(path):
            # Mock ZIP reference file
            return pd.DataFrame({
                "zip": ["10001", "90210"],
                "state_id": ["NY", "CA"],
                "county_name": ["New York", "Los Angeles"],
                "lat": [40.7128, 34.0522],
                "lng": [-74.0060, -118.2437]
            })
        else:
            # Mock properties file (10001 will match NYC, 90210 will not)
            return pd.DataFrame({
                "zip_code": ["10001", "90210"],
                "property_id": [1, 2]
            })

    def fake_to_csv(self, path, *args, **kwargs):
        saved["path"] = path
        saved["rows"] = len(self)

    # Apply the monkeypatches
    monkeypatch.setattr(pd, "read_csv", fake_read_csv)
    monkeypatch.setattr(pd.DataFrame, "to_csv", fake_to_csv)

    # Call with all 3 required positional arguments
    create_ny_only_csv("properties.csv", "zips.csv", "output.csv")

    # Assertions
    assert saved["path"] == "output.csv"
    assert saved["rows"] == 1