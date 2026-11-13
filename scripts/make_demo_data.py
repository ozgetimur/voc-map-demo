"""Generate the SYNTHETIC demo data in data/ (not real measurements).

Run once:  python scripts/make_demo_data.py
"""
import csv
import random
from pathlib import Path

random.seed(42)
DATA = Path(__file__).resolve().parent.parent / "data"

# name, country, lat, lon, site_type  (approximate public coordinates)
SITES = [
    ("Jülich", "Germany", 50.91, 6.41, "suburban"),
    ("Cologne", "Germany", 50.94, 6.96, "urban"),
    ("Paris", "France", 48.86, 2.35, "urban"),
    ("London", "United Kingdom", 51.51, -0.13, "urban"),
    ("Ispra", "Italy", 45.81, 8.63, "suburban"),
    ("Hyytiälä", "Finland", 61.85, 24.29, "forest"),
    ("Istanbul", "Türkiye", 41.01, 28.98, "urban"),
    ("Los Angeles", "USA", 34.05, -118.24, "urban"),
    ("Houston", "USA", 29.76, -95.37, "urban"),
    ("Toronto", "Canada", 43.65, -79.38, "urban"),
    ("Mexico City", "Mexico", 19.43, -99.13, "urban"),
    ("Manaus (ATTO)", "Brazil", -2.14, -59.00, "forest"),
    ("São Paulo", "Brazil", -23.55, -46.63, "urban"),
    ("Santiago", "Chile", -33.45, -70.67, "urban"),
    ("Lagos", "Nigeria", 6.52, 3.38, "urban"),
    ("Nairobi", "Kenya", -1.29, 36.82, "urban"),
    ("Cape Town", "South Africa", -33.92, 18.42, "suburban"),
    ("Cape Verde Observatory", "Cabo Verde", 16.86, -24.87, "remote"),
    ("Delhi", "India", 28.61, 77.21, "urban"),
    ("Beijing", "China", 39.90, 116.40, "urban"),
    ("Seoul", "South Korea", 37.57, 126.98, "urban"),
    ("Tokyo", "Japan", 35.68, 139.69, "urban"),
    ("Danum Valley", "Malaysia", 4.98, 117.84, "forest"),
    ("Sydney", "Australia", -33.87, 151.21, "urban"),
    ("Mauna Loa", "USA", 19.54, -155.58, "remote"),
]

# compound -> typical mean mixing ratio range (ppb) per site type (illustrative)
RANGES = {
    "isoprene":     {"urban": (0.1, 0.8), "suburban": (0.3, 1.5), "forest": (1.5, 6.0), "remote": (0.01, 0.1)},
    "monoterpenes": {"urban": (0.05, 0.4), "suburban": (0.1, 0.6), "forest": (0.3, 1.5), "remote": (0.01, 0.05)},
    "toluene":      {"urban": (0.8, 4.0), "suburban": (0.3, 1.2), "forest": (0.02, 0.2), "remote": (0.005, 0.05)},
    "benzene":      {"urban": (0.3, 2.0), "suburban": (0.1, 0.6), "forest": (0.02, 0.15), "remote": (0.01, 0.05)},
    "methanol":     {"urban": (3.0, 10.0), "suburban": (2.0, 7.0), "forest": (2.0, 8.0), "remote": (0.5, 2.0)},
}
YEARS = [2023, 2024, 2025]

with open(DATA / "sites.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["site_id", "name", "country", "lat", "lon", "site_type"])
    for i, s in enumerate(SITES, start=1):
        w.writerow([i, *s])

with open(DATA / "measurements.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["site_id", "compound", "year", "mean_ppb", "n_samples"])
    for i, (_, _, _, _, stype) in enumerate(SITES, start=1):
        compounds = random.sample(list(RANGES), k=random.randint(2, 5))
        for comp in sorted(compounds):
            for year in random.sample(YEARS, k=random.randint(1, 3)):
                lo, hi = RANGES[comp][stype]
                w.writerow([i, comp, year, round(random.uniform(lo, hi), 3), random.randint(50, 5000)])
print("Wrote", DATA / "sites.csv", "and", DATA / "measurements.csv")
