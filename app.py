"""VOC Map Demo – a small Flask app with a searchable map and CSV download.

Local run:       python app.py
Production run:  gunicorn "app:create_app()"
"""
import csv
import io
import logging
import os
from pathlib import Path

from flask import Flask, Response, abort, g, jsonify, render_template, request

import db

BASE_DIR = Path(__file__).resolve().parent


def create_app(db_path=None):
    app = Flask(__name__)
    # Settings come from environment variables, not hard-coded values.
    app.config["DB_PATH"] = db_path or os.environ.get("VOC_DB_PATH", str(BASE_DIR / "voc_demo.sqlite"))
    app.config["DATA_DIR"] = os.environ.get("VOC_DATA_DIR", str(BASE_DIR / "data"))

    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))

    # Build the database on first start if it does not exist yet.
    if not Path(app.config["DB_PATH"]).exists():
        app.logger.info("Building database at %s", app.config["DB_PATH"])
        db.build_database(app.config["DB_PATH"], app.config["DATA_DIR"])

    def get_conn():
        if "conn" not in g:
            g.conn = db.connect(app.config["DB_PATH"])
        return g.conn

    @app.teardown_appcontext
    def close_conn(_exc):
        conn = g.pop("conn", None)
        if conn is not None:
            conn.close()

    def read_filters():
        """Read ?compound=…&site_type=… and reject unknown values (input validation)."""
        conn = get_conn()
        compound = request.args.get("compound") or None
        site_type = request.args.get("site_type") or None
        if compound and compound not in db.list_values(conn, "compound"):
            abort(400, description=f"Unknown compound: {compound}")
        if site_type and site_type not in db.list_values(conn, "site_type"):
            abort(400, description=f"Unknown site_type: {site_type}")
        return compound, site_type

    @app.get("/")
    def index():
        conn = get_conn()
        return render_template(
            "index.html",
            compounds=db.list_values(conn, "compound"),
            site_types=db.list_values(conn, "site_type"),
        )

    @app.get("/api/sites")
    def api_sites():
        """Return matching sites as GeoJSON (the standard format for map data)."""
        compound, site_type = read_filters()
        rows = db.query_measurements(get_conn(), compound, site_type)

        sites = {}
        for r in rows:
            site = sites.setdefault(r["site_id"], {
                "type": "Feature",
                # GeoJSON order is [longitude, latitude]
                "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
                "properties": {"name": r["name"], "country": r["country"],
                               "site_type": r["site_type"], "measurements": []},
            })
            site["properties"]["measurements"].append(
                {k: r[k] for k in ("compound", "year", "mean_ppb", "n_samples")}
            )
        return jsonify({"type": "FeatureCollection", "features": list(sites.values())})

    @app.get("/download.csv")
    def download_csv():
        """Download the currently filtered data as a CSV file."""
        compound, site_type = read_filters()
        rows = db.query_measurements(get_conn(), compound, site_type)
        buf = io.StringIO()
        fields = ["name", "country", "lat", "lon", "site_type", "compound", "year", "mean_ppb", "n_samples"]
        writer = csv.DictWriter(buf, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        app.logger.info("CSV download: compound=%s site_type=%s rows=%d", compound, site_type, len(rows))
        return Response(
            buf.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=voc_demo_data.csv"},
        )

    @app.get("/health")
    def health():
        """Simple check that hosting platforms / monitoring can call."""
        get_conn().execute("SELECT 1")
        return {"status": "ok"}

    @app.errorhandler(400)
    def bad_request(err):
        return jsonify(error=err.description), 400

    return app


if __name__ == "__main__":
    # Development server only – never use debug=True in production.
    create_app().run(debug=os.environ.get("FLASK_DEBUG") == "1", port=5000)
