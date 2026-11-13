import pandas as pd

from src import peek as peek_module


def test_peek_loads_dataframe(tmp_path, monkeypatch):
    """Verify module load creates a DataFrame from CSV data."""

    # Setup a mock data file using tmp_path so DATA_FILE exists during the test
    mock_csv = tmp_path / "data_ny_properties_only.csv"
    mock_csv.write_text("col1,col2\nval1,val2\n")

    # Patch DATA_FILE in peek_module to point to our temporary file
    monkeypatch.setattr(peek_module, "DATA_FILE", mock_csv)

    # Assert that preview_data successfully loads and returns a dataframe
    df = peek_module.preview_data(rows=5)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
