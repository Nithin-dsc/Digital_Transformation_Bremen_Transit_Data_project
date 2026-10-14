
## 1: ##
 The collect_data_to_csv.py script transformed the raw 5-minute snapshot CSV files into processed_transit_data.csv.



## 2: ##

The `clean_data.py` snippet performs **five key data transformations** to make your GTFS dataset reliable and analysis-ready:

---

# 1. Snapshot Deduplication

* **The Problem:** Because snapshot files are captured every 5 minutes, a vehicle parked at a stop for 7 or 10 minutes gets recorded multiple times in different CSV files for the exact same trip and stop.
* **The Fix:** The script groups by `(trip_id, stop_id)` and keeps only the **last (most recent) observation**, preventing artificial inflation of sample sizes.

---

# 2. Outlier & Noise Removal

* **The Problem:** Real-time feeds occasionally suffer from sensor glitches, system crashes, or cancelled trips that output nonsensical delays (e.g., 300 minutes late or 50 minutes early).
* **The Fix:** It filters out extreme noise, keeping delays strictly within realistic operational bounds:

$$\text{Delay Filter: } -15 \text{ minutes} \le \text{delay\_minutes} \le 120 \text{ minutes}$$



---

# 3. Invalid Timestamp & Coordinate Cleanup

* **The Problem:** Unreadable timestamp strings or corrupt coordinate records (`NaN` or `0.0` for latitude/longitude) will break Plotly maps and Pandas datetime operations.
* **The Fix:** Drops any row where `departure_timestamp` cannot be parsed into a valid date/time, or where spatial coordinates (`stop_lat`, `stop_lon`) are missing or zero.

---

# 4. Vehicle Type Categorization

* **The Problem:** The raw GTFS lookup table uses numeric identifiers (`0` and `3`) for transit modes.
* **The Fix:** Maps those codes directly into clear text categories:
* `0` $\rightarrow$ **Tram**
* `3` $\rightarrow$ **Bus**



---

# 5. Time-Feature Extraction

* **The Problem:** Raw timestamps (e.g., `2026-08-17 14:35:00`) are inconvenient for grouping delays by time of day or day of week.
* **The Fix:** Automatically creates three helper columns:
* `hour`: The hour of day (`0–23`) for rush-hour analysis.
* `day_name`: The day of the week (e.g., *Monday*, *Tuesday*).
* `is_weekend`: Boolean flag (`True`/`False`) to isolate weekend vs. weekday delay patterns.

