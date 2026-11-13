# This file pulls info from the main csv for NYC only.
import os

import pandas as pd

from src.logging_config import get_logger

logger = get_logger(__name__)

def create_ny_only_csv(properties_csv_path, zips_csv_path, output_csv_path):
    """Filter dataset to NY cases and save as CSV with robust validation."""

    logger.info("🧹 Filtering for New York only...")

    # File existence checks
    if not os.path.exists(properties_csv_path):
        logger.info(f"The properties file at '{properties_csv_path}' was not found.")
        return
    if not os.path.exists(zips_csv_path):
        logger.info(f"The zip code reference file at '{zips_csv_path}' was not found.")
        return

    try:
        # Load dataframes safely with specific exception handling for Ruff compliance
        prop_df = pd.read_csv(properties_csv_path, low_memory=False)
        zips_df = pd.read_csv(zips_csv_path, low_memory=False)

    except (FileNotFoundError, PermissionError) as e:
        logger.error(f"File access error encountered: {e}")

    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse CSV formatting: {e}")
        return

    # 3. Schema validation (required columns check)
    required_prop_cols = ["zip_code"]
    required_zip_cols = ["zip", "state_id", "county_name", "lat", "lng"]

    for col in required_prop_cols:
        if col not in prop_df.columns:
            logger.error(f"Required column '{col}' missing from properties dataset.")
            return

    for col in required_zip_cols:
        if col not in zips_df.columns:
            logger.error(f"Required column '{col}' missing from zip reference dataset.")
            return


    def clean_zip(val):
        """Robust ZIP code cleaning and sanitization"""

        if pd.isna(val):
            return ""
        s = str(val).split(".")[0].strip()
        return s.zfill(5) if s.isdigit() and len(s) <= 5 else ""

    # Clean zip columns in both dataframes to prevent string matching issues
    prop_df["zip_code"] = prop_df["zip_code"].apply(clean_zip)
    zips_df["zip"] = zips_df["zip"].apply(clean_zip)

    # Filter the zip reference down to only the 5 NY official counties
    nyc_counties = ["New York", "Kings", "Queens", "Bronx", "Richmond"]
    nyc_zips = zips_df[(zips_df["state_id"] == "NY") & (zips_df["county_name"].isin(nyc_counties))]

    if nyc_zips.empty:
        logger.error("No ZIP codes matched the specified NY counties in the reference dataset.")
        return

    logger.info(f" Filtering listings against {len(nyc_zips)} official NYC ZIP codes..")

    # Merge the two CSV's together on the ZIP code column
    nyc_properties = pd.merge(
        prop_df,
        nyc_zips[["zip", "county_name", "lat", "lng"]],
        left_on="zip_code",
        right_on="zip",
        how="inner"
    )

    if nyc_properties.empty:
        print("The resulting merged NYC properties dataset is empty.")
        return
    
    # Clean up duplicate columns if necessary
    if "zip" in nyc_properties.columns:
        nyc_properties.drop(columns=["zip"], inplace=True)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_csv_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Save the NYC file
    nyc_properties.to_csv(output_csv_path, index=False)
    logger.info(f" Success! created {output_csv_path} with {len(nyc_properties):,} rows restricted entirely to NYC.")


# Build cleaned NYC property dataset
create_ny_only_csv(
    properties_csv_path="data/ny_properties_only.csv",
    zips_csv_path="data/uszips.csv",
    output_csv_path="data/nyc_properties_clean.csv"
)
