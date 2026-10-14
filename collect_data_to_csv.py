import os
import glob
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
DATA_DIR = os.path.join(BASE_DIR, "Data")
RAW_CSV_DIR = os.path.join(DATA_DIR, "raw_5min_csvs")
OUTPUT_CSV = os.path.join(DATA_DIR, "processed_transit_data.csv")

def find_lookup_file():
    possible_paths = [
        os.path.join(DATA_DIR, "bremen_lookup.csv"),
        os.path.join(DATA_DIR, "lookup_table.csv"),
        os.path.join(BASE_DIR, "bremen_lookup.csv"),
        os.path.join(BASE_DIR, "lookup_table.csv")
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    lookup_matches = glob.glob(os.path.join(DATA_DIR, "*lookup*.csv")) + glob.glob(os.path.join(BASE_DIR, "*lookup*.csv"))
    if lookup_matches:
        return lookup_matches[0]
        
    return None

def main():
    lookup_file = find_lookup_file()
    if not lookup_file:
        print("ERROR: Lookup file not found! Place 'bremen_lookup.csv' in the project folder or inside 'Data'.")
        return

    print(f"Using lookup file: {lookup_file}")

    csv_files = glob.glob(os.path.join(DATA_DIR, "**", "*.csv"), recursive=True)
    csv_files = [f for f in csv_files if not f.endswith("processed_transit_data.csv") and "lookup" not in os.path.basename(f).lower()]

    if not csv_files:
        print(f"ERROR: No CSV files found inside '{DATA_DIR}'.")
        return

    print(f"Loading {len(csv_files):,} raw GTFS snapshot CSV files...")

    dfs = []
    for idx, f in enumerate(csv_files, start=1):
        try:
            temp_df = pd.read_csv(f)
            dfs.append(temp_df)
        except Exception as e:
            print(f"Skipping corrupt file {f}: {e}")
        
        if idx % 1000 == 0:
            print(f"Loaded {idx}/{len(csv_files)} files...")

    combined_df = pd.concat(dfs, ignore_index=True)

    print("Cleaning columns and converting timestamps...")
    combined_df = combined_df.rename(columns={
        "timestamp_fetched": "departure_timestamp"
    })

    combined_df = combined_df.dropna(subset=["delay_seconds"])
    combined_df["departure_timestamp"] = pd.to_datetime(combined_df["departure_timestamp"], errors="coerce")
    combined_df["delay_minutes"] = combined_df["delay_seconds"] / 60.0

    print("Merging with lookup table metadata...")
    lookup_df = pd.read_csv(lookup_file)
    
    combined_df["stop_id"] = combined_df["stop_id"].astype(str)
    lookup_df["stop_id"] = lookup_df["stop_id"].astype(str)

    final_df = combined_df.merge(lookup_df, on="stop_id", how="inner")

    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"Exporting compiled dataset to: {OUTPUT_CSV}")
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSUCCESS! Exported {len(final_df):,} total rows to '{OUTPUT_CSV}'.")

if __name__ == "__main__":
    main()


