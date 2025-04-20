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

1. **Install Python**
Download and install Python from the official website: [Download Python](https://www.python.org/downloads/))

2. **Install Dependencies**
All dependencies are automatically installed via `App.bat`, but for reference, the script uses:
   - openrouteservice
   - pandas
   - tqdm

3. **Configure the API Key**
Obtain an API key from the OpenRouteService Dashboard: https://openrouteservice.org/ (requires login).
Copy it into the `example_config.json` file and rename it to `config.json`:

    ```json
    {
        "ORS_API_KEY": "your_ors_api_key"
    }
    ```

4. **Add Coordinates**
Create or modify the `coordinates.json` file in the root directory. Refer to `example_coordinates.json` for the correct format (name, latitude, longitude).

## How to Run

1. **Download and Extract**
Download the ZIP source code and extract it to your desktop.

2. **Run the Script**
   - Double-click `App.bat`
   - Or run it from the command line:

        ```cmd
        App.bat
        ```

- Alternatively, if you're using an IDE, you can run `Script.py` directly (make sure Python is installed).
