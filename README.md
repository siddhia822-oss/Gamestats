# GameStats — Gaming Performance & Hardware Analyzer

A beginner-friendly Streamlit frontend for the provided GameStats GTA 5 dataset and analysis outputs.

## Features

- Dark, neon-accented dashboard
- Overview KPI cards
- Player leaderboard with ranking choices
- FPS, CPU, GPU, RAM, and temperature charts
- Correlation heatmap and statistical insights
- Sidebar filters for game, mode, and player
- CSV upload and downloads
- Dataset explorer and missing-value report

## Run on Windows 10

1. Install Python 3.10 or newer from https://www.python.org/downloads/
   - During installation, tick **Add Python to PATH**.
2. Extract the downloaded ZIP.
3. Open the extracted `GameStats_Frontend` folder.
4. Double-click `run_gamestats.bat`.
5. Wait for installation to finish. A browser tab should open with the dashboard.

If the batch file does not work:
1. Open the project folder in File Explorer.
2. Click the address bar, type `cmd`, and press Enter.
3. Run these commands one at a time:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -r requirements.txt
   py -m streamlit run app.py
   ```

## Dataset

The app defaults to `data/gta5_cleaned_data.csv` and includes the supplied analysis CSV files. You can upload another compatible CSV from the sidebar.

Expected columns include `Player`, `Game`, `Game_Mode`, `Kills`, `Deaths`, `Assists`, `Wins`, `Matches`, `FPS_Avg`, `FPS_Min`, `CPU_Usage`, `GPU_Usage`, `RAM_Usage_GB`, `GPU_Temp`, and `Score`.

## Important limitation

The uploaded backend notebook performs offline data analysis; it does not currently expose HTTP API endpoints. This frontend reads CSV data. It does **not** measure live FPS, temperatures, or sensor values. To connect to a FastAPI backend later, add API endpoints and replace the CSV-loading functions with HTTP requests.

The included dataset may be synthetic. Do not present synthetic readings as measurements from real gaming hardware.

## GitHub

Commit the whole project folder to your shared repository. Avoid committing virtual environments (`.venv`) or secrets.
