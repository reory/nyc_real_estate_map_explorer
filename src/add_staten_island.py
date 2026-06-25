import pandas as pd

# Define paths (Adjust the large file name if it's different!)
large_csv_path = "data/ny_properties_only.csv" 
target_csv_path = "data/nyc_properties_clean.csv"

print("🔍 Searching for Staten Island data...")

try:
    # Read the large file
    large_df = pd.read_csv(large_csv_path)
    
    # Isolate Staten Island rows
    si_rows = large_df[
        (large_df['state'].str.lower() == 'new york') & 
        (large_df['city'].str.lower().str.contains('staten|tottenville|st\. george', na=False))
    ].copy()
    
    if si_rows.empty:
        print("❌ Could not find Staten Island rows in the large CSV file.")
    else:
        print(f"🎯 Found {len(si_rows)} Staten Island rows!")
        
        # Read your existing app CSV to match column names perfectly
        target_df = pd.read_csv(target_csv_path)
        
        # Standardize columns to match what your ingestion script expects
        # (Mapping 'lat' and 'lng' if they are named differently in the large file)
        if 'latitude' in si_rows.columns and 'lat' not in si_rows.columns:
            si_rows['lat'] = si_rows['latitude']
        if 'longitude' in si_rows.columns and 'lng' not in si_rows.columns:
            si_rows['lng'] = si_rows['longitude']
            
        # Keep only the columns your app uses
        si_rows = si_rows[si_rows.columns.intersection(target_df.columns)]
        
        # Append and save!
        combined_df = pd.concat([target_df, si_rows], ignore_index=True)
        combined_df.to_csv(target_csv_path, index=False)
        
        print(f"🎉 Success! Combined file now has {len(combined_df):,} total rows.")
        print(f"📂 Updated file saved at: {target_csv_path}")

except Exception as e:
    print(f"❌ Error occurred: {e}")