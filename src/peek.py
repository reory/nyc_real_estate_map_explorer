"""
Inspect the primary CSV dataset to verify column 
alignment with the USAProperty database schema.
"""

from pathlib import Path

import pandas as pd

from src.logging_config import get_logger

logger = get_logger(__name__)

DATA_FILE = Path("data_ny_properties_only.csv")


def preview_data(rows=20):
    """
    Load and return a preview DataFrame 
    of the specified number of rows from the data file.
    """

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"File not found: {DATA_FILE}"
        )
    
    return pd.read_csv(
        DATA_FILE,
        nrows=rows
    )


def main():
    """
    Execute the data preview workflow and print 
    the head of the dataset to the console.
    """

    df = preview_data()
    logger.info(df.head())


if __name__ == '__main__':
    main()