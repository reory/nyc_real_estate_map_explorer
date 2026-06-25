import pandas as pd
from .database import Session, USAProperty, engine, Base

# Initialize the database
Base.metadata.create_all(engine)
session = Session()


def ingest():
    """Merges property data with coordinates and saves to the database."""

    print("🚀 Starting Ingestion with Coordinate Recovery...")

    # Merge coordinates onto properties
    print("🔗 Loading New York city properties...")
    merged = pd.read_csv("data/nyc_properties_clean.csv")

    # Ingest into Database
    count = 0
    for _, row in merged.iterrows():
        # IMPORTANT: Use the lat/lng from the uszips file (zips)
        latitude = row.get("lat")
        longitude = row.get("lng")

        if pd.isna(latitude) or pd.isna(longitude):
            continue

        prop = USAProperty(
            status=row["status"],
            price=row["price"],
            bed=row["bed"],
            bath=row["bath"],
            acre_lot=row["acre_lot"],
            city=row["city"],
            state=row["state"],
            zip_code=str(row["zip_code"]).split(".")[0].zfill(5),
            house_size=row["house_size"],
            prev_sold_date=str(row["prev_sold_date"]),
            latitude=float(latitude),
            longitude=float(longitude),
        )
        session.add(prop)
        count += 1

        # Commit in batches of 10,000 for speed
        if count % 10000 == 0:
            session.commit()
            print(f"✅ Saved {count} properties...")

    session.commit()
    print(f"😁 Done! {count} properties with coordinates are now in the database.")


if __name__ == "__main__":
    ingest()
