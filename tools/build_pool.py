"""Gera pool.js: pontos aleatórios sobre ruas de Goiânia (OpenStreetMap), onde quase sempre há Street View.
Uso (da pasta goiania-geo):  python tools/build_pool.py [roads.json] [boundary.json]
Sem argumentos, baixa tudo do Overpass e do Nominatim."""
import json, math, random, sys, time, urllib.parse, urllib.request

N_POINTS = 4000
UA = {"User-Agent": "goiania-geo-personal"}
OVERPASS = ["https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"]
QUERY = ('[out:json][timeout:180][bbox:-16.83,-49.45,-16.45,-49.07];'
         'way["highway"~"^(trunk|primary|secondary|tertiary|residential|unclassified|living_street)$"];out geom qt;')

def fetch(url, data=None):
    req = urllib.request.Request(url, data=data, headers=UA)
    return json.load(urllib.request.urlopen(req, timeout=240))

def load_roads(path):
    if path:
        return json.load(open(path, encoding="utf-8"))
    wait = 15
    for _ in range(6):
        for srv in OVERPASS:
            try:
                return fetch(srv, urllib.parse.urlencode({"data": QUERY}).encode())
            except Exception as e:
                print("Overpass falhou:", srv, e)
        time.sleep(wait)
        wait *= 2
    sys.exit("Overpass indisponível, tente mais tarde.")

def load_boundary(path):
    data = json.load(open(path, encoding="utf-8")) if path else fetch(
        "https://nominatim.openstreetmap.org/lookup?osm_ids=R334547&format=json&polygon_geojson=1&polygon_threshold=0.0005")
    return [(lat, lng) for lng, lat in data[0]["geojson"]["coordinates"][0]]

def inside(lat, lng, poly):
    ok = False
    for i in range(len(poly)):
        (yi, xi), (yj, xj) = poly[i], poly[i - 1]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            ok = not ok
    return ok

def main():
    roads = load_roads(sys.argv[1] if len(sys.argv) > 1 else None)
    poly = load_boundary(sys.argv[2] if len(sys.argv) > 2 else None)

    # Trechos de rua dentro de Goiânia, com o comprimento de cada um
    segs, lens = [], []
    k = math.cos(math.radians(16.7))
    for way in roads["elements"]:
        g = way.get("geometry") or []
        for a, b in zip(g, g[1:]):
            if not inside((a["lat"] + b["lat"]) / 2, (a["lon"] + b["lon"]) / 2, poly):
                continue
            segs.append((a["lat"], a["lon"], b["lat"], b["lon"]))
            lens.append(math.hypot(b["lat"] - a["lat"], (b["lon"] - a["lon"]) * k))
    print(len(segs), "trechos de rua")

    # Sorteio proporcional ao comprimento: cada metro de rua tem a mesma chance
    pts = []
    for la1, ln1, la2, ln2 in random.choices(segs, weights=lens, k=N_POINTS):
        t = random.random()
        pts.append([round(la1 + t * (la2 - la1), 6), round(ln1 + t * (ln2 - ln1), 6)])

    with open("pool.js", "w", encoding="utf-8") as fh:
        fh.write("// Gerado por tools/build_pool.py — pontos [lat, lng] sobre ruas de Goiânia\nconst PHOTO_POOL = ")
        json.dump(pts, fh, separators=(",", ":"))
        fh.write(";\n")
    print(len(pts), "pontos salvos em pool.js")

main()
