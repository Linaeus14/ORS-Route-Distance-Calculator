# ORS Route Distance Calculator

This Python script calculates and exports driving distances and estimated travel times between a list of places using the OpenRouteService (ORS) API.

It generates all possible route permutations between the listed locations. For example, if you have locations A, B, and C, it will check the distance and time required for:

- A → A, A → B, A → C
- B → A, B → B, B → C
- C → A, C → B, C → C

## Features

- Calculates pairwise distances and durations
- Exports results to Excel
- Automatically skips completed or invalid routes
- Built-in retry handling and rate limit backoff
- Outputs both step-by-step logs and summary data

## Setup

1. **Install Python (No need to install if using App.exe)**

    Download and install Python from the official website: [python.org](https://www.python.org/downloads/)

    All dependencies are automatically installed via `App.bat` and are bundled into `App.exe`, but for reference, the script uses:
   - openrouteservice
   - pandas
   - tqdm

2. **Configure the API Key**

    Obtain an API key from the OpenRouteService Dashboard: [openrouteservice.org](https://openrouteservice.org/) (requires login).
    Copy it into the `example_config.json` file and rename it to `config.json`:

    ```json
    {
        "ORS_API_KEY": "your_ors_api_key"
    }
    ```

3. **Add Coordinates**

    Create or modify the `coordinates.json` file in the root directory. Refer to `example_coordinates.json` for the correct format (name, latitude, longitude):

    ```json
    [
        { "name": "Location A", "coords": [-1.277472, 116.83025] },
        { "name": "Location B", "coords": [-1.269167, 116.832861] }
    ]
    ```

## How to Run

1. **Download and Extract**

    Download the ZIP source code or the `App.exe` release from the GitHub Releases page and extract it to your desktop.

2. **Run the Script**

   - **Option 1: Using the `.bat` file**
     - Ensure that `coordinates.json` and `config.json` are in the same directory as the `App.bat` file.
     - Double-click `App.bat`
     - Alternatively, if you're using an IDE, you can run `Script.py` directly (make sure Python and dependencies are installed).
     - Or run it from the command line:

        ```cmd
        App.bat
        ```

   - **Option 2: Using the release application**
     - Ensure that `coordinates.json` and `config.json` are in the same directory as the `App.exe` file.
     - Double-click `App.exe` to run the program.

Both options function the same way and require the `coordinates.json` and `config.json` files in the root folder.
