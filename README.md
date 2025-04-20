# ORS Route Distance Calculator

This Python script calculates and exports driving distances and estimated travel times between a list of places using the OpenRouteService API.

## Features

- Calculates pairwise distances and durations
- Saves data to Excel
- Automatically skips completed or invalid routes in the given list
- Retry handling and rate limit backoff
- Step-by-step and summary exports

## Setup

1. Install python: [Python](https://www.python.org/downloads/)

    Python Depedency (Auto Install is included in App.bat):
    - openrouteservice
    - pandas
    - tqdm

2. Add your OpenRouteService API key from thier [API Dashboard](https://openrouteservice.org/) (require login) to `example_config.json` then rename it into `config.json`:

    ```JSON
    {
        "ORS_API_KEY": "your ors api key"
    }
    ```

3. Place/Make your `coordinates.json` file in the root directory, check `example_coordinates.json` for the format of name, latitude, and longitude.

## Run

Open it normally by double clicking or Run the App.bat on your cmd:

```cmd
App.bat
```

Alternatively you can run Script.py if you have an IDE with a pyhon interperter installed.
