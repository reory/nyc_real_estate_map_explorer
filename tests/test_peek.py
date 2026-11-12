import importlib

import pandas as pd

import src.peek as peek_module


def test_peek_loads_dataframe(monkeypatch):
    """Verify module load creates a DataFrame from CSV data."""

    fake_df = pd.DataFrame({"a": [1, 2, 3]})

    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: fake_df)

    importlib.reload(peek_module)

    assert hasattr(peek_module, "df")
    assert isinstance(peek_module.df, pd.DataFrame)
    assert list(peek_module.df.columns) == ["a"]
