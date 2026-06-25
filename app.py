import os
import datetime
import math
import streamlit as st
from streamlit_folium import st_folium
from src.database import get_filtered_properties
from src.mapping import generate_full_map
from src.engine import analyse_properties
from src.analytics import (
    generate_borough_price_box,
    generate_size_vs_price_scatter,
    clean_borough_name,
)

def apply_local_css(file_path):
    """Function to inject custom CSS safely."""
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            st.markdown(f"<style>{f.read()}<style>", unsafe_allow_html=True)

# Page configuration
st.set_page_config(layout="wide", page_title="NYC Real Estate Explorer.")

# Initialise the session state for theme configuration
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

st.sidebar.header("Display Settings")

# Dark Mode toggle button switch
st.sidebar.toggle("Dark Mode", key="dark_mode")

# Apply style sheet based on toggle status
if st.session_state.dark_mode:
    apply_local_css("assets/dark_mode.css")
else:
    apply_local_css("assets/silver_mode.css")

# This calculates the system time on the server thread instantly during execution
current_time = datetime.datetime.now()
date_string = current_time.strftime("%A, %B %d, %Y")
time_string = current_time.strftime("%I:%M %p")

# Wrapped in a class wrapper for CSS targeting
st.markdown(
    f'<div class="top-clock-widget">📅 {date_string} &nbsp;|&nbsp; ⏰ {time_string}</div>', 
    unsafe_allow_html=True
)

# App header title
st.title("🏡 NYC Real Estate Explorer")

# Initialize session state for filters
if "min_price" not in st.session_state:
    st.session_state.min_price = 0
if "max_price" not in st.session_state:
    st.session_state.max_price = 1500000
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = None
if "show_map" not in st.session_state:
    st.session_state.show_map = False

# Sidebar Controls
st.sidebar.header("Filter Properties")
min_price = st.sidebar.slider(
    "Min Price", 0, 1500000, st.session_state.min_price
)
max_price = st.sidebar.slider(
    "Max Price", 0, 1500000, st.session_state.max_price
)

# Borough dropdown
borough_filter = st.sidebar.selectbox(
    "Boroughs",
    ["All Boroughs", "Manhattan", "Brooklyn", "Queens", "The Bronx", "Staten Island"]
)


# Filter application with callback
def apply_filters():
    st.session_state.min_price = min_price
    st.session_state.max_price = max_price
    st.session_state.filtered_data = get_filtered_properties(
        st.session_state.min_price, st.session_state.max_price
    )
    st.session_state.show_map = True


# Fetch Data - apply filters
if st.sidebar.button("Apply Filter"):
    with st.spinner("Querying database and building map.."):
        apply_filters()

# Display results
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

        # Convert back to list of dictionaries for the mapper
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

        if not plot_data:
            st.warning(
                f" 🚫 No properties found in **{borough_filter} for this specific price range. Please expand your sidebar sliders."
            )
            st.markdown(f"""
            **Current Search Parameters:**
            * Borough: **{borough_filter}**
            * Price Range: **${st.session_state.min_price:,.0f}** - **${st.session_state.max_price:,.0f}**
            
            Try expanding your price range options or selecting another borough.
            """)
        else:
            st.success(f"✅ Found {len(plot_data)} properties.")

        # Create a map placeholder
        map_container = st.container()

        # Generate the map using the cleaned data
        nyc_map = generate_full_map(properties=plot_data[:1000])

        # Render the map inside a container
        with map_container:
            st_folium(
                nyc_map,
                width=None,
                height=600,
                key="nyc_map_static",
                returned_objects=[],
            )
        st.markdown("---")
        st.header(" Advanced Analytics")

        col1, col2 = st.columns(2)

        with col1:
            with st.spinner("Generating House Price Distributions..."):
                box_chart = generate_borough_price_box(processed_df)
                st.plotly_chart(box_chart, width="stretch")

        with col2:
            with st.spinner("Generating House Sizes..."):
                scatter_chart = generate_size_vs_price_scatter(processed_df)
                st.plotly_chart(scatter_chart, width="stretch")

    else:
        st.warning("🚫 No properties found for this price range.")

        # UI feedback
        st.markdown(f"""
        **Current Search:**
        * Price Range: **${st.session_state.min_price:,.0f}** - **${st.session_state.max_price:,.0f}**
        
        **Suggestion:**
        Try narrowing your price range or clearing the filters to see more listings.
        """)

        # Clear button
        if st.button("Reset Filters"):
            st.session_state.min_price = 0
            st.session_state.max_price = 1500000
            st.rerun()
else:
    st.info(
        "Adjust the filters in the sidebar and click 'Apply Filters' to explore."
    )