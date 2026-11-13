import plotly.express as px


def clean_borough_name(row):
    """
    Maps all messy NYC neighborhood text strings directly to 
    their official 5 boroughs using a high-speed lookup map.
    """

    # Standardise inputs
    city = str(row.get("city", "")).strip().title()  # e.g., "bed stuy" -> "Bed Stuy"
    county = str(row.get("county_name", "")).lower().strip()
    
    # Check County Strings First
    if "kings" in county or "brooklyn" in county: 
        return "Brooklyn"
    if "queens" in county: 
        return "Queens"
    if "new york" in county or "manhattan" in county: 
        return "Manhattan"
    if "bronx" in county: 
        return "Bronx"
    if "richmond" in county or "staten island" in county: 
        return "Richmond"

    # Comprehensive Neighborhood Map
    neighborhood_map = {
        # --- BROOKLYN ---
        "Bed Stuy": "Brooklyn", "Bedstuy": "Brooklyn", "Brownville": "Brooklyn", 
        "Kensington": "Brooklyn", "Crown Heights": "Brooklyn", "Flatbush": "Brooklyn", 
        "Prosp Leff Gdns": "Brooklyn", "East Flatbush": "Brooklyn", "Stuyvesant Hts": "Brooklyn", 
        "Canarsie": "Brooklyn", "Bath Beach": "Brooklyn", "Dyker Heights": "Brooklyn", 
        "Bedford": "Brooklyn", "Brighton Beach": "Brooklyn", "Old Mill Basin": "Brooklyn", 
        "Sheepshead Bay": "Brooklyn", "Gowanus": "Brooklyn", "Flatlands": "Brooklyn", 
        "Bushwick": "Brooklyn", "Ocean Hill": "Brooklyn", "Gerritsen Beach": "Brooklyn", 
        "Gravesend": "Brooklyn", "City Line": "Brooklyn", "Cypress Hills": "Brooklyn",
        "Brooklyn": "Brooklyn", "Bedstuy Brooklyn": "Brooklyn", "Brooklyn Heights": "Brooklyn",
        "East New York": "Brooklyn",

        # --- QUEENS ---
        "Middle Village": "Queens", "Jackson Heights": "Queens", "Corona": "Queens", 
        "Long Island City": "Queens", "Maspeth": "Queens", "Glendale": "Queens", 
        "Elmhurst": "Queens", "Woodside": "Queens", "East Elmhurst": "Queens", 
        "Ridgewood": "Queens", "Sunnyside": "Queens", "Rego Park": "Queens", 
        "College Point": "Queens", "Astoria": "Queens", "Flushing": "Queens", 
        "Woodhaven": "Queens", "Howard Beach": "Queens", "Saint Albans": "Queens", 
        "Forest Hills": "Queens", "Beechhurst": "Queens", "Jamaica": "Queens", 
        "Briarwood": "Queens", "Kew Gardens Hills": "Queens", "Ozone Park": "Queens", 
        "Fresh Meadows": "Queens", "Kew Gardens": "Queens", "Whitestone": "Queens", 
        "South Ozone Park": "Queens", "Hollis": "Queens", "Bayside": "Queens", 
        "Springfield Gardens": "Queens", "South Ozone": "Queens", "Malba": "Queens", 
        "Addisleigh Park": "Queens", "Hillcrest": "Queens", "Kew Garden Hills": "Queens", 
        "Lindenwood Howard Beach": "Queens", "Oakland Gardens": "Queens", "Douglaston": "Queens", 
        "Jamaica Estates": "Queens", "Hollis Hills": "Queens", "Rockaway Beach": "Queens", 
        "Rockaway Park": "Queens", "Arverne": "Queens", "Broad Channel": "Queens", 
        "Far Rockaway": "Queens", "Belle Harbor": "Queens", "Breezy Point": "Queens", 
        "Cambria Heights": "Queens", "Rosedale": "Queens", "Laurelton": "Queens", 
        "Bellerose": "Queens", "Floral Park": "Queens", "Little Neck": "Queens", 
        "Glen Oaks": "Queens", "Holliswood": "Queens", "Bellerose Manor": "Queens", 
        "Jamaica South": "Queens", "Oueens": "Queens", "Edgemere": "Queens", 
        "Arverne By The Sea": "Queens", "Neponsit": "Queens", "Queens": "Queens",
        "Queens Village North": "Queens", "Richmond Hill South": "Queens", 
        "Richmond Hill": "Queens", "Queens Village": "Queens", 
        "South Richmond Hill": "Queens", "Queens Village Jamaica": "Queens",

        # --- MANHATTAN ---
        "Manhattan": "Manhattan", "New York": "Manhattan", "Ny": "Manhattan", 
        "Nyc": "Manhattan", "Roosevelt Island": "Manhattan", "New York City": "Manhattan",

        # --- BRONX ---
        "Bronx": "Bronx", "Riverdale": "Bronx", "Williambridge": "Bronx", 
        "Wakefield": "Bronx", "Eastchester": "Bronx",

        # --- RICHMOND ---
        "Staten Island": "Richmond", "Richmond": "Richmond", 
        "Tottenville": "Richmond", "St. George": "Richmond", 
        "Arden": "Richmond", "Huguenot": "Richmond"
    }

    # Route via our map lookup
    if city in neighborhood_map:
        return neighborhood_map[city]

    # Fallback for true geographic outsiders
    city_lower = city.lower()
    if "brooklyn" in city_lower:
        return "Brooklyn"
    if "queens" in city_lower: 
        return "Queens"
    if "manhattan" in city_lower or "new york" in city_lower: 
        return "Manhattan"
    if "bronx" in city_lower: 
        return "Bronx"
    if "staten island" in city_lower or "richmond" in city_lower: 
        return "Richmond"

    if any(out in city_lower for out in ["white plains", "champlain", "accord", "pelham", "atlantique", "manorville", "woodstock", "cairo", "bronxville"]):
        return "Outside NYC"
    return "Other NYC"


def generate_borough_price_box(df):
    """Generate a box plot showing price distributions per borough."""
    
    # Create a copy and build the Borough column dynamically
    local_df = df.copy()
    local_df["Borough"] = local_df.apply(clean_borough_name, axis=1)
    local_df = local_df[local_df["Borough"] != "Outside NYC"]

    fig = px.box(
        local_df,
        x ="Borough",
        y ="price",
        color="Borough",
        title=" 💵 Property Price Distribution by Borough",
        labels={"Borough": "Borough", "Price": "Price ($)"},
        points="outliers",
    )

    # Layout updates
    fig.update_layout(
        yaxis_type="log", # Handles extreme prices gracefully
        showlegend=False,
        template="plotly_white",
    )

    return fig


def generate_size_vs_price_scatter(df):
    """Generate a scatter plot comparing house sizes to price."""

    local_df = df.copy()
    local_df["Borough"] = local_df.apply(clean_borough_name, axis=1)
    local_df = local_df[local_df["Borough"] != "Outside NYC"]

    # Filter out rows with missing sizes to keep the plot manageable
    clean_df = local_df[local_df["house_size"].notna() & (local_df["house_size"] > 0) & (local_df["house_size"] < 10000)]

    # Compare property size and price by borough
    fig = px.scatter(
        clean_df,
        x="house_size",
        y="price",
        color="Borough",
        hover_data=["city"],
        title="🏡 House Size vs Total Listing Price",
        labels={"house_size": "Size (Sq Ft)", "price": "Price ($)"},
        opacity=0.6,
    )

    fig.update_layout(template="plotly_white")
    return fig


# -------------------------------------------------------------------------------
    # DEBUG PRINT DIAGNOSTIC
    #print("\n🔍 --- TARGETING 'OTHER NYC' STRINGS ---")
    #other_df = local_df[local_df["Borough"] == "Other NYC"]
    #if not other_df.empty:
        #print("Exact unique cities found:", other_df["city"].unique().tolist())
        #print("Exact unique counties found:", other_df["county_name"].unique().tolist())
   # else:
        #print("No records left in Other NYC!")
    #print("---------------------------------------------------\n")
# -----------------------------------------------------------------------------