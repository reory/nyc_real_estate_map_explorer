import logging

import pandas as pd
import pytest

from src import add_staten_island


def test_add_staten_island_success(monkeypatch, tmp_path):
    """
    Verify Staten Island rows are successfully extracted,
    standardised, and appended to the target dataset.
    """

    # Setup temporary data files and directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    large_csv = data_dir / "ny_properties_only.csv"
    target_csv = data_dir / "nyc_properties_clean.csv"

    # Write mock large CSV containing Staten Island rows with latitude/longitude
    large_csv.write_text(
        "state,city,price,latitude,longitude\n"
        "New York,Staten Island,450000,40.5795,-74.1502\n"
        "New York,Manhattan,900000,40.7831,-73.9712\n"
    )

    # Write mock target clean CSV
    target_csv.write_text(
        "state,city,price,lat,lng\n"
        "New York,Manhattan,900000,40.7831,-73.9712\n"
    )

    monkeypatch.setattr(add_staten_island, "LARGE_CSV", large_csv)
    monkeypatch.setattr(add_staten_island, "TARGET_CSV", target_csv)

    add_staten_island.add_staten_island_data()

    # Verify target CSV was updated with Staten Island row and lat/lng standardised
    updated_df = pd.read_csv(target_csv)

    assert len(updated_df) == 2
    assert "Staten Island" in updated_df["city"].values
    assert "lat" in updated_df.columns
    assert "lng" in updated_df.columns


def test_add_staten_island_missing_columns(monkeypatch, tmp_path):
    """
    Ensure a ValueError is raised when required
    schema columns are missing from the source data.
    """

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    large_csv = data_dir / "ny_properties_only.csv"
    target_csv = data_dir / "nyc_properties_clean.csv"

    # Large CSV missing required 'state' column
    large_csv.write_text(
        "city,price\n"
        "Staten Island,450000\n"
    )

    target_csv.write_text("state,city,price\n")

    monkeypatch.setattr(add_staten_island, "LARGE_CSV", large_csv)
    monkeypatch.setattr(add_staten_island, "TARGET_CSV", target_csv)

    with pytest.raises(ValueError, match="Missing required columns"):
        add_staten_island.add_staten_island_data()


def test_add_staten_island_no_matches(monkeypatch, tmp_path, caplog):
    """
    Confirm graceful handling and
    zero rows added when no Staten Island records are found.
    """

    caplog.set_level(logging.WARNING)

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    large_csv = data_dir / "ny_properties_only.csv"
    target_csv = data_dir / "nyc_properties_clean.csv"

    # No Staten Island matching rows
    large_csv.write_text(
        "state,city,price\n"
        "New York,Albany,300000\n"
    )

    target_csv.write_text("state,city,price\n")

    monkeypatch.setattr(add_staten_island, "LARGE_CSV", large_csv)
    monkeypatch.setattr(add_staten_island, "TARGET_CSV", target_csv)

    added_count = add_staten_island.add_staten_island_data()

    assert added_count == 0
    assert "Could not find Staten Island rows" in caplog.text
