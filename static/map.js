// Draw the map, fetch GeoJSON from /api/sites and redraw when filters change.
const map = L.map("map").setView([20, 10], 2);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const COLORS = { urban: "#c0392b", suburban: "#e67e22", forest: "#27ae60", remote: "#2980b9" };
let layer = null;

function currentQuery() {
  const params = new URLSearchParams();
  const compound = document.getElementById("compound").value;
  const siteType = document.getElementById("site_type").value;
  if (compound) params.set("compound", compound);
  if (siteType) params.set("site_type", siteType);
  return params.toString();
}

function popupHtml(p) {
  const rows = p.measurements
    .map(m => `<tr><td>${m.compound}</td><td>${m.year}</td><td>${m.mean_ppb}</td></tr>`)
    .join("");
  return `<strong>${p.name}</strong> (${p.country})<br><em>${p.site_type}</em>
    <table><tr><th>Compound</th><th>Year</th><th>ppb</th></tr>${rows}</table>`;
}

async function refresh() {
  const query = currentQuery();
  document.getElementById("download").href = "/download.csv" + (query ? "?" + query : "");

  const res = await fetch("/api/sites" + (query ? "?" + query : ""));
  if (!res.ok) {
    document.getElementById("count").textContent = "Error loading data";
    return;
  }
  const geojson = await res.json();

  if (layer) map.removeLayer(layer);
  layer = L.geoJSON(geojson, {
    pointToLayer: (feature, latlng) => L.circleMarker(latlng, {
      radius: 7, weight: 1, color: "#333", fillOpacity: 0.85,
      fillColor: COLORS[feature.properties.site_type] || "#777",
    }),
    onEachFeature: (feature, l) => l.bindPopup(popupHtml(feature.properties)),
  }).addTo(map);

  document.getElementById("count").textContent = `${geojson.features.length} sites`;
}

document.getElementById("compound").addEventListener("change", refresh);
document.getElementById("site_type").addEventListener("change", refresh);
refresh();
