# This file pulls info from the main csv for NYC only.

import pandas as pd


def create_ny_only_csv(properties_csv_path, zips_csv_path, output_csv_path):
    """Filter dataset to NY cases and save as CSV"""

    print("🧹 Filtering for New York only...")

    # Load zip code reference file
    prop_df = pd.read_csv(properties_csv_path)
    zips_df = pd.read_csv(zips_csv_path)

    # Clean zip columns in both dataframes to prevent string matching issues
    prop_df["zip_code"] = prop_df["zip_code"].astype(str).str.split(".").str[0].str.zfill(5)
    zips_df["zip"] = zips_df["zip"].astype(str).str.split(".").str[0].str.zfill(5)

    # Filter the zip reference down to only the 5 NY official counties
    nyc_counties = ["New York", "Kings", "Queens", "Bronx", "Richmond"]
    nyc_zips = zips_df[(zips_df["state_id"] == "NY") & (zips_df["county_name"].isin(nyc_counties))]

    print(f" Filtering listings against {len(nyc_zips)} official NYC ZIP codes..")

    # Merge the two CSV's together on the ZIP code column
    nyc_properties = pd.merge(
        prop_df,
        nyc_zips[["zip", "county_name", "lat", "lng"]],
        left_on="zip_code",
        right_on="zip",
        how="inner"
    )
    
    # Clean up duplicate columns if necessary
    nyc_properties.drop(columns=["zip"], inplace=True)

    # Save the NYC file
    nyc_properties.to_csv(output_csv_path, index=False)
    print(f" Success! created {output_csv_path} with {len(nyc_properties):,} rows restricted entirely to NYC.")


create_ny_only_csv(
    properties_csv_path="data/ny_properties_only.csv",
    zips_csv_path="data/uszips.csv",
    output_csv_path="data/nyc_properties_clean.csv"
)
