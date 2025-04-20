import openrouteservice
import sys
import json
import time
import os
import csv
import pandas as pd
from collections import OrderedDict
from tqdm import tqdm
from datetime import datetime
from openrouteservice.exceptions import ApiError
import warnings

# Suppress the specific warning for rate limits
warnings.filterwarnings("ignore", message="Rate limit exceeded.*")

# ========== CONFIG ==========
with open("config.json", "r") as f:
    config = json.load(f)
ORS_API_KEY = config["ORS_API_KEY"]
SAVE_INTERVAL = 10
TIMESTAMP = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
CSV_FILENAME = "data/ors_routes_backup.csv"
EXCEL_FILENAME = f"export/ors_routes_{TIMESTAMP}.xlsx"
SUMMARY_FILENAME = f"export/ors_routes_summary_{TIMESTAMP}.xlsx"
PAIR_STATE_FILE = "data/completed_pairs.json"
SKIPPED_FILE = "data/skipped_no_route.json"
RETRY_LIMIT = 5
RETRY_BACKOFF = 2
RATE_LIMIT_SLEEP = 2
PROFILE = "driving-car"
# ============================

# Ensure the data and export folders exist
os.makedirs("data", exist_ok=True)
os.makedirs("export", exist_ok=True)

client = openrouteservice.Client(key=ORS_API_KEY)

# Load towns from JSON
with open("coordinates.json", "r", encoding="utf-8") as f:
    towns_data = json.load(f)
towns = [(t["name"], t["coords"][::-1])
         for t in towns_data]  # ORS expects [lon, lat]

# Load or initialize completed_pairs
if os.path.exists(PAIR_STATE_FILE):
    with open(PAIR_STATE_FILE, "r", encoding="utf-8") as f:
        completed_pairs = {tuple(pair) for pair in json.load(f)}
else:
    completed_pairs = set()

# Load skipped pairs to avoid retrying known no-routes
if os.path.exists(SKIPPED_FILE):
    with open(SKIPPED_FILE, "r", encoding="utf-8") as f:
        skipped_pairs = {tuple(pair) for pair in json.load(f)}
else:
    skipped_pairs = set()

# Recover from existing CSV (in case of missing pair state file)
if os.path.exists(CSV_FILENAME) and not completed_pairs:
    with open(CSV_FILENAME, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            completed_pairs.add((row['From'], row['To']))
            completed_pairs.add((row['To'], row['From']))

# Prepare all permutations
pairs = [(from_town, to_town) for from_town in towns for to_town in towns]
all_routes = []
counter = 0

for (from_name, from_coords), (to_name, to_coords) in tqdm(pairs, desc="Processing"):
    if (from_name, to_name) in completed_pairs or (from_name, to_name) in skipped_pairs:
        continue

    success = False
    attempts = 0

    while not success and attempts < RETRY_LIMIT:
        try:
            route = client.directions(
                coordinates=[from_coords, to_coords],
                profile=PROFILE,
                format='json'
            )
            leg = route['routes'][0]['segments'][0]
            steps = leg.get('steps', [])

            all_routes.extend([{
                'From': from_name,
                'To': to_name,
                'Instruction': step['instruction'],
                'Distance': f"{step['distance'] / 1000:.2f} km",
                'Time': f"{step['duration'] / 60:.1f} min"
            } for step in steps])

            completed_pairs.add((from_name, to_name))
            success = True
            counter += 1
            time.sleep(RATE_LIMIT_SLEEP)

        except ApiError as e:
            err_str = str(e).lower()
            if 'Could not find' in err_str or '2010' in err_str:
                print(f"No route or invalid location: {from_name} -> {to_name}. Skipping.")
                skipped_pairs.add((from_name, to_name))
                break
            else:
                attempts += 1
                wait = RETRY_BACKOFF ** attempts
                print(f"API Error {from_name} -> {to_name}: {e}, retrying in {wait}s")
                time.sleep(wait)

        except Exception as e:
            attempts += 1
            wait = RETRY_BACKOFF ** attempts
            print(f"Unexpected error {from_name} -> {to_name}: {e}, retrying in {wait}s")
            time.sleep(wait)

    if counter >= SAVE_INTERVAL:
        with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['From', 'To', 'Instruction', 'Distance', 'Time'])
            if f.tell() == 0:
                writer.writeheader()
            writer.writerows(all_routes)
        all_routes.clear()
        counter = 0

        with open(PAIR_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(list(completed_pairs), f, indent=2)
        with open(SKIPPED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(skipped_pairs), f, indent=2)

# Final Save
if all_routes:
    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['From', 'To', 'Instruction', 'Distance', 'Time'])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(all_routes)

with open(PAIR_STATE_FILE, "w", encoding="utf-8") as f:
    json.dump(list(completed_pairs), f, indent=2)
with open(SKIPPED_FILE, "w", encoding="utf-8") as f:
    json.dump(list(skipped_pairs), f, indent=2)

# Excel Export
expected_total = len(pairs)
with open(CSV_FILENAME, encoding='utf-8') as f:
    completed_total = sum(1 for _ in f) - 1

if completed_total >= expected_total:
    df = pd.read_csv(CSV_FILENAME)
    df.to_excel(EXCEL_FILENAME, index=False)
    print(f"Step-by-step exported to {EXCEL_FILENAME}")

    summary_data = OrderedDict()
    for _, row in df.iterrows():
        key = (row['From'], row['To'])
        if key not in summary_data:
            summary_data[key] = {'Distance': 0.0, 'Time': 0.0}
        summary_data[key]['Distance'] += float(row['Distance'].strip(' km'))
        summary_data[key]['Time'] += float(row['Time'].strip(' min'))

    summary_rows = [{
        'From': from_to[0],
        'To': from_to[1],
        'Distance': f"{data['Distance']:.2f} km",
        'Time': f"{data['Time']:.1f} min"
    } for from_to, data in summary_data.items()]

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_excel(SUMMARY_FILENAME, index=False)
    print(f"Summary exported to {SUMMARY_FILENAME}")
else:
    print(f"\nIncomplete: {completed_total}/{expected_total} routes.")
