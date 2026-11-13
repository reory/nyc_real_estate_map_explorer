from pathlib import Path

import pandas as pd

from src.logging_config import get_logger

from .database import Base, Session, USAProperty, engine

logger = get_logger(__name__)

DATA_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "nyc_properties_clean.csv"
)

BATCH_SIZE = 10_000


def ingest():
    """Merges property data with coordinates and saves to the database."""

    # Initialise the database
    Base.metadata.create_all(engine)

    session = Session()

    logger.info("🚀 Starting Ingestion with Coordinate Recovery...")

    try:

        # Merge coordinates onto properties
        logger.info("🔗 Loading New York city properties...")

        merged = pd.read_csv(DATA_FILE)

        inserted = 0
        skipped = 0

        # Ingest into Database
        for _, row in merged.iterrows():

        # IMPORTANT: Use the lat/lng from the uszips file (zips)
            latitude = row.get("lat")
            longitude = row.get("lng")

            if pd.isna(latitude) or pd.isna(longitude):
                skipped += 1
                continue

            # Validate coordinates
            try:
                latitude = float(latitude)
                longitude = float(longitude)

            except (TypeError, ValueError):
                skipped += 1
                continue

            # Validate ranges
            if not (-90 <= latitude <= 90):
                skipped += 1
                continue

            if not (-180 <= longitude <= 180):
                skipped += 1
                continue

            price = row.get("price")

            if pd.isna(price):
                skipped += 1
                continue

            if price < 0:
                skipped += 1
                continue

            city = str(row.get("city", "")).strip()

            state = str(row.get("state", "")).strip()

            if not city:
                skipped += 1
                continue

            if not state:
                skipped += 1
                continue

            zip_code = row.get("zip_code")

            if pd.isna(zip_code):
                skipped += 1
                continue

            # Create property record from source data
            prop = USAProperty(
                status=row["status"],
                price=price,
                bed=row["bed"],
                bath=row["bath"],
                acre_lot=row["acre_lot"],
                city=city,
                state=state,
                county_name=row["county_name"],
                zip_code=str(zip_code).split(".")[0].zfill(5),
                house_size=row["house_size"],
                prev_sold_date=str(row["prev_sold_date"]),
                latitude=latitude,
                longitude=longitude,
            ) 
            session.add(prop)
            
            inserted += 1

            # Commit in batches of 10,000 for speed
            if inserted % BATCH_SIZE == 0:
                session.commit()
                logger.info(f"✅ Saved {inserted:,} properties...")

        # Final commit for any remaining records
        session.commit()

        logger.info("😁 Done! " 
            f"{inserted} properties. " 
            f"Skipped {skipped} invalid records."
        )
    
    except Exception:

        session.rollback()
        raise

    finally:
        session.close()

if __name__ == "__main__":
    ingest()
