import csv
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    # Each test gets its own fresh database in a temporary folder.
    app = create_app(db_path=str(tmp_path / "test.sqlite"))
    app.config["TESTING"] = True
    return app.test_client()


def test_index_page_loads(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"VOC Map Demo" in res.data


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_api_returns_geojson(client):
    data = client.get("/api/sites").get_json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    lon, lat = data["features"][0]["geometry"]["coordinates"]
    assert -180 <= lon <= 180 and -90 <= lat <= 90


def test_filter_by_compound(client):
    data = client.get("/api/sites?compound=isoprene").get_json()
    for feature in data["features"]:
        compounds = {m["compound"] for m in feature["properties"]["measurements"]}
        assert compounds == {"isoprene"}


def test_unknown_filter_is_rejected(client):
    res = client.get("/api/sites?compound=DROP TABLE sites")
    assert res.status_code == 400


def test_csv_download_matches_filter(client):
    res = client.get("/download.csv?site_type=forest")
    assert res.status_code == 200
    assert res.mimetype == "text/csv"
    rows = list(csv.DictReader(io.StringIO(res.get_data(as_text=True))))
    assert rows and all(r["site_type"] == "forest" for r in rows)
