# GameStats — GTA 5 Performance & Hardware Analyzer

GameStats is a Streamlit dashboard and a Jupyter Notebook analysis project using the same CSV dataset.

## Files
- `app.py` — Streamlit dashboard and interactive visualizations.
- `game_stats.csv` — the provided 300-row dataset used by both the dashboard and notebook.
- `GameStats_Backend.ipynb` — data cleaning, derived metrics, descriptive statistics, group analysis, leaderboard, correlations, and charts.
- `requirements.txt` — Python dependencies.
- `index.html`, `style.css`, `script.js` — optional standalone HTML/CSS/JavaScript frontend files, if you want to retain them in the final submission. They are not used by the Streamlit app unless separately integrated.

## Run locally
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud
1. Push the project files to a GitHub repository.
2. In Streamlit Community Cloud, create/select an app and set the main file path to `app.py`.
3. Ensure `game_stats.csv` is in the repository root, next to `app.py`.
4. Deploy.

## Notebook
Open `GameStats_Backend.ipynb` in Jupyter or Google Colab. Keep `game_stats.csv` beside the notebook when running locally. In Colab, upload the same CSV when prompted.

**Important data note:** the CSV is sample/synthetic project data, not verified measurements collected from actual GTA 5 gameplay or live hardware sensors. The app and notebook analyze the supplied records; they do not access live PC hardware.
