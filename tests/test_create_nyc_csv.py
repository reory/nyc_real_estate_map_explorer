# Mock pandas so no real CSV files are touched.

import pandas as pd
from src.create_nyc_csv import create_ny_only_csv


def test_create_nyc_only_csv(monkeypatch):

    df = pd.DataFrame({"state": ["New York", "Brooklyn"], "value": [1, 2]})

    def fake_read_csv(path):

        return df

    saved = {}

    def fake_to_csv(self, path, *args, **kwargs):

        saved["path"] = path
        saved["rows"] = len(self)

    monkeypatch.setattr("pandas.read_csv", fake_read_csv)
    monkeypatch.setattr("pandas.DataFrame.to_csv", fake_to_csv)

    create_ny_only_csv("input.csv", "output.csv")

    assert saved["path"] == "output.csv"
    assert saved["rows"] == 1
