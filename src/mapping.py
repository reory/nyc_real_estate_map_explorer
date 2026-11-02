import math

import folium
import streamlit as st
from folium.plugins import MarkerCluster


def get_hex_color(price):
    """Returns a hex color string based on NYC real estate price tiers."""

    # Missing data - not listed.
    if price is None or (isinstance(price, float) and math.isnan(price)):
        return "#7f8c8d"

    # Entry level: Affordable (under $450k)
    if price < 450_000:
        return "#2ecc71"

    # Mid Market: mid/high standard ($450k - $1.2m)
    elif price < 1_200_000:
        return "#e67e22"

    # Luxury: High end real estate ($1.2m and above)
    else:
        return "#e74c3c"


@st.cache_resource
def generate_full_map(properties=None):
    """Build complete NYC map with all scraped case markers"""

    if not properties:
        print("⚠️ No properties found!")
        return None

    # Start the folium map.
    nyc_map = folium.Map(
        location=[40.7128, -74.0060],
        zoom_start=9,
        tiles="cartodbpositron",
        prefer_canvas=True,
    )

    # Create the cluster group.
    marker_cluster = MarkerCluster().add_to(nyc_map)

    # Helper function to identify missing, blank, or NaN data formats safely
    def is_missing(val):
        return (
            val is None
        or (isinstance(val, float) and math.isnan(val))
        or (isinstance(val, str) and val.strip().lower() in ("nan", "n/a", ""))
    )

    # Build map markers
    for prop in properties:

        lat = prop.get("latitude")
        lon = prop.get("longitude")

        # Skip if coordinates are missing
        if is_missing(lat) or is_missing(lon):
            continue

        price = prop.get("price")
        color_hex = get_hex_color(price)
        
        # Price Display formatting
        p_price_text = "Unlisted" if is_missing(price) else f"${float(price):,.0f}"

        # Beds (removes trailing floating decimals safely: 3.0 -> 3)
        bed_val = prop.get("bed")
        p_bed = "N/A" if is_missing(bed_val) else (f"{int(float(bed_val))}" if float(bed_val).is_integer() else f"{bed_val}")

        # Baths (handles halves gracefully: 2.5 remains 2.5, 2.0 -> 2)
        bath_val = prop.get("bath")
        p_bath = "N/A" if is_missing(bath_val) else (f"{int(float(bath_val))}" if float(bath_val).is_integer() else f"{bath_val}")

        # Living Area
        size_val = prop.get("house_size")
        p_size = "N/A" if (is_missing(size_val) or float(size_val) <= 0) else f"{float(size_val):,.0f} sqft"

        # Lot Size
        lot_val = prop.get("acre_lot")
        p_lot = "N/A" if (is_missing(lot_val) or float(lot_val) <= 0) else f"{float(lot_val):.2f} acres"

        # Create a HTML popup.
        popup_text = f"""
        <div style="font-family: Arial, sans-serif; min-width: 150px;">
            <h3 style="margin-bottom: 5px; color: #2c3e50;">{p_price_text}</h3>
            <hr style="margin: 5px 0; border: 0; border-top: 1px solid #eee;">
            <b>Beds:</b> {p_bed}<br>
            <b>Baths:</b> {p_bath}<br>
            <b>Living Area:</b> {p_size}<br>
            <b>Lot Size:</b> {p_lot}<br>
            <b>City:</b> {prop.get('city', 'N/A')}<br>
            <b>Borough:</b> {prop.get('borough', 'N/A')}<br>
        </div>
        """

        # CircleMarker
        folium.CircleMarker(
            location=[float(lat), float(lon)],
            radius=5,
            popup=folium.Popup(popup_text, max_width=200),
            color=color_hex,
            fill=True,
            fill_color=color_hex,
            fill_opacity=0.7,
        ).add_to(marker_cluster)

    # Define the Floating Legend HTML
    legend_html = """
     <div style="
     position: fixed; 
     bottom: 50px; left: 20px; width: 220px; height: auto; 
     background-color: white; border: 2px solid #bdc3c7; z-index: 9999; 
     font-size: 14px; font-family: sans-serif;
     border-radius: 10px; padding: 15px;
     box-shadow: 2px 2px 12px rgba(0,0,0,0.2);
     ">
     <b style="color: #2c3e50; font-size: 16px;">Property Price Tiers</b><br><br>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <i style="background: #2ecc71; width: 14px; height: 14px; border-radius: 50%; display: inline-block; margin-right: 12px;"></i>
         <span>Under $450k</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <i style="background: #e67e22; width: 14px; height: 14px; border-radius: 50%; display: inline-block; margin-right: 12px;"></i>
         <span>$450k - $1.2M</span>
     </div>
     <div style="display: flex; align-items: center; margin-bottom: 8px;">
         <i style="background: #e74c3c; width: 14px; height: 14px; border-radius: 50%; display: inline-block; margin-right: 12px;"></i>
         <span>Over $1.2M</span>
     </div>
     <div style="display: flex; align-items: center;">
         <i style="background: #7f8c8d; width: 14px; height: 14px; border-radius: 50%; display: inline-block; margin-right: 12px;"></i>
         <span>Unlisted / No Data</span>
     </div>
     </div>
     """

    # Add it to the map
    nyc_map.get_root().html.add_child(folium.Element(legend_html))

    # Return the map object instead of saving it
    return nyc_map