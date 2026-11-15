# VOC Map Demo

A small web app that shows VOC measurement sites on a world map. You can filter the sites and download the data as CSV.

**Live demo:** https://voc-map-demo.onrender.com

![tests](https://github.com/ozgetimur/voc-map-demo/actions/workflows/ci.yml/badge.svg)

>  The data is **synthetic** (generated for practice) and is not real measurement data.

## How it works
- **Backend:** Python (Flask) + SQLite database
- **Frontend:** Leaflet map in JavaScript
- The map asks the backend for data (`/api/sites`) and draws the sites.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py
```
Then open http://127.0.0.1:5000

## Run tests
```bash
pytest -q
```

## Deployment
The app is hosted on Render. Every push to GitHub runs the tests and updates the live site.