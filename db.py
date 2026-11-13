"""Database helpers: build the SQLite database from the CSV files and query it."""
import csv
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS sites (
    site_id   INTEGER PRIMARY KEY,
    name      TEXT NOT NULL,
    country   TEXT NOT NULL,
    lat       REAL NOT NULL,
    lon       REAL NOT NULL,
    site_type TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS measurements (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id   INTEGER NOT NULL REFERENCES sites(site_id),
    compound  TEXT NOT NULL,
    year      INTEGER NOT NULL,
    mean_ppb  REAL NOT NULL,
    n_samples INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_meas_compound ON measurements(compound);
CREATE INDEX IF NOT EXISTS idx_meas_site ON measurements(site_id);
"""


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


def build_database(db_path, data_dir):
    """Create the database file from data/sites.csv and data/measurements.csv."""
    data_dir = Path(data_dir)
    conn = connect(db_path)
    with conn:
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM measurements")
        conn.execute("DELETE FROM sites")
        with open(data_dir / "sites.csv", encoding="utf-8") as f:
            conn.executemany(
                "INSERT INTO sites VALUES (:site_id, :name, :country, :lat, :lon, :site_type)",
                csv.DictReader(f),
            )
        with open(data_dir / "measurements.csv", encoding="utf-8") as f:
            conn.executemany(
                "INSERT INTO measurements (site_id, compound, year, mean_ppb, n_samples) "
                "VALUES (:site_id, :compound, :year, :mean_ppb, :n_samples)",
                csv.DictReader(f),
            )
    conn.close()


def list_values(conn, column):
    """Distinct values for a filter dropdown (column is whitelisted by the caller)."""
    table = "measurements" if column == "compound" else "sites"
    rows = conn.execute(f"SELECT DISTINCT {column} FROM {table} ORDER BY {column}")
    return [r[0] for r in rows]


def query_measurements(conn, compound=None, site_type=None):
    """Return measurement rows joined with their site, optionally filtered.

    Values are passed as SQL parameters (?), never pasted into the query string,
    which protects against SQL injection.
    """
    sql = """
        SELECT s.site_id, s.name, s.country, s.lat, s.lon, s.site_type,
               m.compound, m.year, m.mean_ppb, m.n_samples
        FROM measurements m JOIN sites s ON s.site_id = m.site_id
        WHERE 1 = 1
    """
    params = []
    if compound:
        sql += " AND m.compound = ?"
        params.append(compound)
    if site_type:
        sql += " AND s.site_type = ?"
        params.append(site_type)
    sql += " ORDER BY s.name, m.compound, m.year"
    return [dict(r) for r in conn.execute(sql, params)]
