import os
import sys
import json
import time
import csv
from collections import OrderedDict
from datetime import datetime
import warnings

# Dependencies
from tqdm import tqdm
from pandas import read_csv, DataFrame
from openrouteservice import Client
from openrouteservice.exceptions import ApiError

# ========== CONFIG ==========
with open("config.json", "r") as f:
    config = json.load(f)
ORS_API_KEY = config["ORS_API_KEY"]
SAVE_INTERVAL = 10
TIMESTAMP = sys.argv[1] if len(
    sys.argv) > 1 else datetime.now().strftime("%d-%m-%Y_%H.%M.%S")
CSV_FILENAME = "data/ors_routes_backup.csv"
EXCEL_FILENAME = f"export/{TIMESTAMP}/ors_routes_{TIMESTAMP}.xlsx"
SUMMARY_FILENAME = f"export/{TIMESTAMP}/ors_routes_summary_{TIMESTAMP}.xlsx"
PAIR_STATE_FILE = "data/completed_pairs.json"
SKIPPED_FILE = "data/skipped_no_route.json"
RETRY_LIMIT = 5
RETRY_BACKOFF = 2
RATE_LIMIT_SLEEP = 2
PROFILE = "driving-car"
# ============================


def load_locations():
    # Load towns from JSON
    with open("coordinates.json", "r", encoding="utf-8") as f:
        locations_data = json.load(f)
    locations = [(t["name"], t["coords"][::-1])
                 for t in locations_data]  # ORS expects [lon, lat]

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
    pairs = [(from_location, to_location)
             for from_location in locations for to_location in locations]

    return [pairs, completed_pairs, skipped_pairs]


def export():
    df = read_csv(CSV_FILENAME)
    df.to_excel(EXCEL_FILENAME, index=False)
    print(f"Step-by-step exported to {EXCEL_FILENAME}")

    summary_data = OrderedDict()
    for _, row in df.iterrows():
        key = (row['From'], row['To'])
        if key not in summary_data:
            summary_data[key] = {'Distance': 0.0, 'Time': 0.0}
        summary_data[key]['Distance'] += float(
            row['Distance'].strip(' km'))
        summary_data[key]['Time'] += float(row['Time'].strip(' min'))

    summary_rows = [{
        'From': from_to[0],
        'To': from_to[1],
        'Distance': f"{data['Distance']:.2f} km",
        'Time': f"{data['Time']:.1f} min"
    } for from_to, data in summary_data.items()]

    summary_df = DataFrame(summary_rows)
    summary_df.to_excel(SUMMARY_FILENAME, index=False)
    print(f"Summary exported to {SUMMARY_FILENAME}")


def process_route(client, from_name, from_coords, to_name, to_coords, completed_pairs, skipped_pairs):
    """Process a single route and return the result."""
    attempts = 0
    while attempts < RETRY_LIMIT:
        try:
            route = client.directions(
                coordinates=[from_coords, to_coords],
                profile=PROFILE,
                format='json'
            )
            leg = route['routes'][0]['segments'][0]
            steps = leg.get('steps', [])
            completed_pairs.add((from_name, to_name))
            return [{
                'From': from_name,
                'To': to_name,
                'Instruction': step['instruction'],
                'Distance': f"{step['distance'] / 1000:.2f} km",
                'Time': f"{step['duration'] / 60:.1f} min"
            } for step in steps]
        except ApiError as e:
            handle_api_error(e, from_name, to_name, skipped_pairs)
            break
        except Exception as e:
            attempts += 1
            wait = RETRY_BACKOFF ** attempts
            print(
                f"\nUnexpected error {from_name} -> {to_name}: {e}, retrying in {wait}s")
            time.sleep(wait)
    return []


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def handle_api_error(e, from_name, to_name, skipped_pairs):
    # sourcery skip: extract-method
    """Handle API errors during route processing."""
    err_str = str(e).lower()
    if 'could not find' in err_str or '2010' in err_str:
        print(
            f"\nNo route or invalid location: {from_name} -> {to_name}. Skipping.")
        skipped_pairs.add((from_name, to_name))
    elif 'quota exceeded' in err_str:
        clear_screen()
        print(f"\nQuota exceeded for the API: {ORS_API_KEY}.")
        print("Saving data and exporting from the last iteration.\n")
        time.sleep(3)
        print("Terminating in 5s. Please wait until the API quota reset before continuing from last save.\n")
        time.sleep(5)
        raise SystemExit


def save_progress(all_routes, completed_pairs, skipped_pairs):
    """Save progress to files."""
    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f, fieldnames=['From', 'To', 'Instruction', 'Distance', 'Time'])
        if f.tell() == 0:
            writer.writeheader()
        writer.writerows(all_routes)

    with open(PAIR_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(list(completed_pairs), f, indent=2)
    with open(SKIPPED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(skipped_pairs), f, indent=2)


def process_all_routes(client, pairs, completed_pairs, skipped_pairs):
    """Process all routes and save progress periodically."""
    all_routes = []
    counter = 0
    for (from_name, from_coords), (to_name, to_coords) in tqdm(pairs, desc="Processing"):
        if (from_name, to_name) in completed_pairs or (from_name, to_name) in skipped_pairs:
            continue

        routes = process_route(client, from_name, from_coords,
                               to_name, to_coords, completed_pairs, skipped_pairs)
        all_routes.extend(routes)
        counter += 1

        if counter >= SAVE_INTERVAL:
            save_progress(all_routes, completed_pairs, skipped_pairs)
            all_routes.clear()
            counter = 0

    # Final save
    if all_routes:
        save_progress(all_routes, completed_pairs, skipped_pairs)


def main():
    # Suppress the specific warning for rate limits
    warnings.filterwarnings("ignore", message="Rate limit exceeded.*")

    # Ensure the data and export folders exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("export", exist_ok=True)
    os.makedirs(f"export/{TIMESTAMP}", exist_ok=True)

    client = Client(key=ORS_API_KEY)
    pairs, completed_pairs, skipped_pairs = load_locations()

    process_all_routes(client, pairs, completed_pairs, skipped_pairs)

    # Check completion and export results
    expected_total = len(pairs)
    with open(CSV_FILENAME, encoding='utf-8') as f:
        completed_total = sum(1 for _ in f) - 1

    if completed_total >= expected_total:
        export()
    else:
        print(f"\nIncomplete: {completed_total}/{expected_total} routes.")


if __name__ == "__main__":
    main()
