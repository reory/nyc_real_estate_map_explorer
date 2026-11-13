import os
from pathlib import Path

import streamlit as st
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH = (
    BASE_DIR
    / "data"
    / "us_real_estate.db"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DATABASE_PATH}"
)

MAX_QUERY_RESULTS = 30_000

# You can update this string to Postgres/MySQL when ready.
engine = create_engine(DATABASE_URL)

# Create the factory and bind it to the db file.
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Create the base class for all database models.
Base = declarative_base()


# This class must inherit from 'Base'
class USAProperty(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    bed = Column(Integer)
    state = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False)
    county_name = Column(String)
    status = Column(String)
    prev_sold_date = Column(String)
    zip_code = Column(String(5))
    bath = Column(Float)
    house_size = Column(Float)
    acre_lot = Column(Float)
    price = Column(Float, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


    def __repr__(self):
        return(
            f"USAProperty("
            f"id={self.id}, "
            f"city='{self.city}', "
            f"price={self.price})"
        )


def initialise_database():
    """Create database tables if they do not already exist."""

    # This tells SQLAlchemy to look at the USAProperty class
    # and create the table in the db file.
    Base.metadata.create_all(engine)


@st.cache_data(ttl=600)
def get_filtered_properties(min_price=None, max_price=None):
    """
    Filter and return properties based on optional
    minimum and maximum price constraints
    """

    session = Session()

    try:
        query = session.query(USAProperty).filter(
            USAProperty.state.ilike("%New York%")
        )

        if (
            min_price is not None
            and 
            max_price is not None
            and 
            min_price > max_price
        ):
            raise ValueError(
                "Minimum price cannot exceed maximum price."
            )

        if min_price is not None and min_price < 0:
            raise ValueError(
        "Minimum price cannot be negative."
        )

        if max_price is not None and max_price < 0:
            raise ValueError(
        "Maximum price cannot be negative."
        )
        
        if min_price is not None:
            query = query.filter(USAProperty.price >= min_price)

        if max_price is not None:
            query = query.filter(USAProperty.price <= max_price)

        results = query.limit(MAX_QUERY_RESULTS + 1).all()

        results = results[:MAX_QUERY_RESULTS]

        # CONVERSION: Convert SQLAlchemy objects to a list of clean dictionaries
        # This makes the data lightweight and easy for Streamlit to cache/serialise
        clean_results = [
            {
                "latitude": p.latitude,
                "longitude": p.longitude,
                "price": p.price,
                "bed": p.bed,
                "bath": p.bath,
                "house_size": p.house_size,
                "acre_lot": p.acre_lot,
                "city": p.city,
                "county_name": p.county_name,
            }
            for p in results
        ]

        return clean_results

    finally:
        session.close()
