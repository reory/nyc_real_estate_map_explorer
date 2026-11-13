from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")

# Define paths (Adjust the large file name if it's different!)
LARGE_CSV = DATA_DIR / "ny_properties_only.csv" 
TARGET_CSV = DATA_DIR / "nyc_properties_clean.csv"


def add_staten_island_data():
    """
    Extract Staten Island property records from 
    the raw dataset and append them to the clean target CSV.
    """

    print("🔍 Searching for Staten Island data...")

    # Read your existing app CSV to match column names perfectly
    large_df = pd.read_csv(LARGE_CSV)
    target_df = pd.read_csv(TARGET_CSV)

    required_columns = {"state", "city"}

    missing = required_columns - set(large_df.columns)

    if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )
    
    # Isolate Staten Island rows
    si_rows = large_df[
        (large_df['state'].fillna("").str.lower() == 'new york') & 
        (large_df['city'].fillna("").str.lower().str.contains(r'staten|tottenville|st\. george', na=False))
    ].copy()

    
    if si_rows.empty:
        print("❌ Could not find Staten Island rows in the large CSV file.")
        return 0

    # Standardise columns to match what your ingestion script expects
    # (Mapping 'lat' and 'lng' if they are named differently in the large file)
    if 'latitude' in si_rows.columns and 'lat' not in si_rows.columns:
        si_rows['lat'] = si_rows['latitude']
    if 'longitude' in si_rows.columns and 'lng' not in si_rows.columns:
        si_rows['lng'] = si_rows['longitude']
            
    # Keep only the columns your app uses
    si_rows = si_rows[
        si_rows.columns.intersection(
            target_df.columns
        )
    ]
        
    # Append and save!
    combined_df = pd.concat(
        [target_df, si_rows], 
        ignore_index=True
        ).drop_duplicates()

    temp_file = TARGET_CSV.with_suffix(".tmp")

    combined_df.to_csv(
        temp_file,
        index=False
    )

    temp_file.replace(TARGET_CSV)
        
    print(f"🎉 Success! Added {len(si_rows):,} rows")
    print(f"📂 Updated file saved at: {TARGET_CSV}")


if __name__ == '__main__':

    try:
        add_staten_island_data()

    except (
        OSError,
        UnicodeDecodeError,
        ValueError,
        pd.errors.EmptyDataError,
        pd.errors.ParserError,
        ) as exc:
        print(f"❌ Error occurred: {exc}")

