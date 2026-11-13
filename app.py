import datetime
import math
import os

import streamlit as st
from streamlit_folium import st_folium

from src.analytics import (
    clean_borough_name,
    generate_borough_price_box,
    generate_size_vs_price_scatter,
)
from src.database import get_filtered_properties
from src.engine import analyse_properties
from src.mapping import generate_full_map

# Dashboard configuration constants
MAX_PRICE_LIMIT = 10_000_000

def apply_local_css(file_path):
    """Function to inject custom CSS safely into the Streamlit page."""
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Page configuration, layout and theme state initialisation
st.set_page_config(layout="wide", page_title="NYC Real Estate Explorer.")

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.sidebar.header("Display Settings")
st.sidebar.toggle("Dark Mode", key="dark_mode")

# Apply style sheet based on toggle status
if st.session_state.dark_mode:
    apply_local_css("assets/dark_mode.css")
else:
    apply_local_css("assets/silver_mode.css")

# Top UTC clock banner and page header
current_time = datetime.datetime.now(datetime.UTC)
date_string = current_time.strftime("%A, %B %d, %Y")
time_string = current_time.strftime("%I:%M %p")

st.markdown(
    f'<div class="top-clock-widget">📅 {date_string} &nbsp;|&nbsp; ⏰ {time_string}</div>', 
    unsafe_allow_html=True
)
st.title("🏡 NYC Real Estate Explorer")

# Initialise session state for filters
if "min_price" not in st.session_state:
    st.session_state.min_price = 0
if "max_price" not in st.session_state:
    st.session_state.max_price = MAX_PRICE_LIMIT
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = None
if "show_map" not in st.session_state:
    st.session_state.show_map = False
if "slider_min" not in st.session_state:
    st.session_state.slider_min = 0
if "slider_max" not in st.session_state:
    st.session_state.slider_max = MAX_PRICE_LIMIT
if "borough_select" not in st.session_state:
    st.session_state.borough_select = "All Boroughs"

# Sidebar price and borough filters
st.sidebar.header("Filter Properties")

min_price = st.sidebar.slider(
    "Min Price", 
    0, 
    MAX_PRICE_LIMIT, 
    format="$%,d",
    key="slider_min",
)

max_price = st.sidebar.slider(
    "Max Price", 
    0, 
    MAX_PRICE_LIMIT,
    format="$%,d",
    key="slider_max",
)

# Borough dropdown
borough_filter = st.sidebar.selectbox(
    "Boroughs",
    ["All Boroughs", "Manhattan", "Brooklyn", "Queens", "The Bronx", "Staten Island"],
    key="borough_select",
)


def apply_filters():
    """Apply user filters and refresh property results."""

    st.session_state.min_price = min_price
    st.session_state.max_price = max_price
    st.session_state.filtered_data = get_filtered_properties(
        st.session_state.min_price, st.session_state.max_price
    )
    st.session_state.show_map = True

def reset_filters():
    """Reset all filter values, widget states, and map visibility before reruns."""

    st.session_state.min_price = 0
    st.session_state.max_price = MAX_PRICE_LIMIT
    st.session_state.slider_min = 0
    st.session_state.slider_max = MAX_PRICE_LIMIT
    st.session_state.borough_select = "All Boroughs"
    st.session_state.filtered_data = None
    st.session_state.show_map = False


# Sidebar action buttons (Apply and Reset)
sidebar_col1, sidebar_col2 = st.sidebar.columns(2)

with sidebar_col1:
    if st.button("Apply Filters", use_container_width=True):
        with st.spinner("Querying database and building map.."):
            apply_filters()

with sidebar_col2:
    st.button("Reset Filters", use_container_width=True, on_click=reset_filters)

# Render interactive map and analytics charts when results are active
if st.session_state.show_map and st.session_state.filtered_data is not None:
    raw_data = st.session_state.filtered_data

    if raw_data:

        # Run the data through Scipy/Pandas
        processed_df = analyse_properties(raw_data)

        # Borough dropdown filter
        processed_df["Borough"] = processed_df.apply(clean_borough_name, axis=1)

        if borough_filter != "All Boroughs":
            if borough_filter == "The Bronx":
                target_name = "Bronx"
            elif borough_filter == "Staten Island":
                target_name = "Richmond"
            else:
                target_name = borough_filter
            processed_df = processed_df[processed_df["Borough"] == target_name]

        # Sanitise NaN float values to "N/A" strings for map tooltips
        raw_plot_data = processed_df.to_dict("records")

        # Scrub NAN values and return them safely into "N/A" for map presentation
        plot_data = []
        for row in raw_plot_data:
            cleaned_row = {}
            for key, val in row.items():

                if isinstance(val, float) and math.isnan(val):
                    cleaned_row[key] = "N/A"
                else:
                    cleaned_row[key] = val
            plot_data.append(cleaned_row)

        # Display search status feedback
        if not plot_data:
            st.warning(
                f" 🚫 No properties found in **{borough_filter}** " 
                "for this specific price range. " 
                "Please expand your sidebar sliders."
            )
            st.markdown(f"""
            **Current Search Parameters:**
            * Borough: **{borough_filter}**
            * Price Range: **${st.session_state.min_price:,.0f}** - **${st.session_state.max_price:,.0f}**
            
            Try expanding your price range options or selecting another borough.
            """)
        else:
            st.success(f"✅ Found {len(plot_data)} properties.")

        # Generate the map using the cleaned data (capped at 1000 markers)
        map_container = st.container()
        nyc_map = generate_full_map(properties=plot_data[:1000])

        with map_container:
            st_folium(
                nyc_map,
                width=None,
                height=600,
                key="nyc_map_static",
                returned_objects=[],
            )
        
        # Render side-by-side Plotly analytics charts
        st.markdown("---")
        st.header(" Advanced Analytics")
        col1, col2 = st.columns(2)

        with col1, st.spinner("Generating House Price Distributions..."):
            box_chart = generate_borough_price_box(processed_df)
            st.plotly_chart(box_chart, width="stretch")

        with col2, st.spinner("Generating House Sizes..."):
            scatter_chart = generate_size_vs_price_scatter(processed_df)
            st.plotly_chart(scatter_chart, width="stretch")

    else:
        # Empty query result state and filter reset control
        st.warning("🚫 No properties found for this price range.")

        # UI feedback
        st.markdown(f"""
        **Current Search:**
        * Price Range: **${st.session_state.min_price:,.0f}** - **${st.session_state.max_price:,.0f}**
        **Suggestion:**
        Try narrowing your price range or clearing the filters to see more listings.
        """)

else:
    st.info(
        "Adjust the filters in the sidebar and click 'Apply Filters' to explore."
    )