
import streamlit as st
from sqlalchemy import Column, Float, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Create the base class for all database models.
Base = declarative_base()


# This class must inherit from 'Base'
class USAProperty(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    bed = Column(Integer)
    state = Column(String)
    city = Column(String)
    county_name = Column(String)
    status = Column(String)
    prev_sold_date = Column(String)
    zip_code = Column(String)
    bath = Column(Float)
    house_size = Column(Float)
    acre_lot = Column(Float)
    price = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)


# You can update this string to Postgres/MySQL when ready.
engine = create_engine("sqlite:///data/us_real_estate.db")

# Create the factory and bind it to the db file.
Session = sessionmaker(bind=engine)

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

        if min_price is not None:
            query = query.filter(USAProperty.price >= min_price)
        if max_price is not None:
            query = query.filter(USAProperty.price <= max_price)

        results = query.limit(30000).all()

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
