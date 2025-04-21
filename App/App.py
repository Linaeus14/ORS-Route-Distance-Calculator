# Import necessary libraries
import os
import sys
import json
import time
import csv
from collections import OrderedDict
from datetime import datetime
import warnings
from tqdm import tqdm
from pandas import read_csv, DataFrame
from openrouteservice import Client
from openrouteservice.exceptions import ApiError

# Function to clear the screen
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

# Function to reset progress data
def reset_progress_data():
    clear_screen()
    print("===========================")
    print("Resetting Progress Data")
    print("===========================")
    print("This will delete previous progress tracking but not exports...")
    data_folder = "data"
    if os.path.exists(data_folder):
        for file in os.listdir(data_folder):
            if file.endswith(".json") or file.endswith(".csv"):
                os.remove(os.path.join(data_folder, file))
    print("Done. You may rerun the calculation from scratch.")
    input("\nPress Enter to return to the main menu...")

# Function to display help
def display_help():
    clear_screen()
    print("===========================")
    print("Help")
    print("===========================")
    print("1. Option 1 runs the calculator.")
    print("2. Option 2 resets only the progress data (pairs, skips), not the final export.")
    print("3. Ensure you have a valid OpenRouteService API key in config.json.")
    print("4. The script has an auto-save after every successful route calculation.")
    print("5. You can continue the progress if it's interrupted or terminated.")
    print("6. Make sure coordinates.json exists in the working folder.")
    print("===========================")
    input("\nPress Enter to return to the main menu...")

# Function to run the main script
def run_script():
    clear_screen()
    print("===========================")
    print("Running the OpenRouteService Distance Calculation")
    print("===========================")
    try:
        # Check if running in a PyInstaller bundle
        if hasattr(sys, '_MEIPASS'):
            # Add the parent directory of the bundled script to sys.path
            sys.path.append(os.path.join(sys._MEIPASS, '..'))
        else:
            # Add the parent directory in a normal Python environment
            sys.path.append(os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..')))

        import script
        script.main()
    except Exception as e:
        print(f"An error occurred while running the script: {e}")
    print("Distance calculation completed. Check the export folder for output.")
    input("\nPress Enter to return to the main menu...")

# Main menu function
def main_menu():
    while True:
        clear_screen()
        print("===========================")
        print("Main Menu")
        print("===========================")
        print("1. Run the OpenRouteService Distance Calculation")
        print("2. Reset Progress Data (not export)")
        print("3. View Help")
        print("4. Exit")
        print("===========================")
        option = input("Choose an option (1/2/3/4): ")

        if option == "1":
            run_script()
        elif option == "2":
            reset_progress_data()
        elif option == "3":
            display_help()
        elif option == "4":
            clear_screen()
            print("Exiting... Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    # Ensure necessary folders exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("export", exist_ok=True)

    # Display the menu
    main_menu()
