"""
Ambil batas 5 provinsi Kalimantan (kode BIG 61-65) dari GeoServices BIG,
lalu simpan sebagai geojson yang siap dipakai FIRELINE (kolom KDPPUM,
WADMPR sesuai yang dibaca fireline/pipeline.py::province_boundaries).

Jalankan dari komputer yang punya akses internet bebas (bukan sandbox ini):
    pip install requests
    python fetch_kalimantan_boundaries.py

Kalau endpoint atau nama layer BIG berubah, sesuaikan BASE_URL / LAYER_ID
di bawah (cek lewat browser: buka BASE_URL, lihat daftar layer & field-nya).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import requests

# Endpoint REST BIG untuk layer batas provinsi (STIG).
BASE_URL = "https://geoservices.big.go.id/gis/rest/services/STIG/Batas_Provinsi/MapServer"
LAYER_ID = 0  # sesuaikan kalau layer batas provinsi bukan index 0

# Kode provinsi Kalimantan (BIG): 61 Kalbar, 62 Kalteng, 63 Kalsel, 64 Kaltim, 65 Kaltara
KALIMANTAN_CODES = ["61", "62", "63", "64", "65"]

OUTPUT_PATH = Path("data/raw/kalimantan_provinces.geojson")


def fetch_layer_fields() -> dict:
    """Cek metadata layer dulu, supaya tahu nama field kode provinsi yang sebenarnya."""
    resp = requests.get(f"{BASE_URL}/{LAYER_ID}", params={"f": "json"}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_geojson(where_clause: str) -> dict:
    params = {
        "where": where_clause,
        "outFields": "*",
        "outSR": "4326",
        "f": "geojson",
    }
    resp = requests.get(f"{BASE_URL}/{LAYER_ID}/query", params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if "features" not in data:
        raise RuntimeError(f"Response tidak berisi 'features': {data}")
    return data


def normalize_fields(geojson: dict, code_field: str, name_field: str) -> dict:
    """Rename field sumber ke KDPPUM / WADMPR kalau nama aslinya beda."""
    for feature in geojson["features"]:
        props = feature["properties"]
        if code_field != "KDPPUM" and code_field in props:
            props["KDPPUM"] = props.pop(code_field)
        if name_field != "WADMPR" and name_field in props:
            props["WADMPR"] = props.pop(name_field)
    return geojson


def main() -> None:
    print(f"Cek metadata layer: {BASE_URL}/{LAYER_ID}")
    try:
        meta = fetch_layer_fields()
        field_names = [f["name"] for f in meta.get("fields", [])]
        print("Field tersedia di layer:", field_names)
    except Exception as exc:  # noqa: BLE001
        print(f"Gagal ambil metadata ({exc}); lanjut coba query langsung dengan asumsi KDPPUM/WADMPR.")
        field_names = ["KDPPUM", "WADMPR"]

    code_field = "KDPPUM" if "KDPPUM" in field_names else next(
        (f for f in field_names if "KDP" in f.upper() or "KODE" in f.upper()), "KDPPUM"
    )
    name_field = "WADMPR" if "WADMPR" in field_names else next(
        (f for f in field_names if "WADM" in f.upper() or "NAMA" in f.upper()), "WADMPR"
    )
    print(f"Pakai field kode = {code_field!r}, field nama = {name_field!r}")

    where = " OR ".join(f"{code_field}='{code}'" for code in KALIMANTAN_CODES)
    print(f"Query: WHERE {where}")

    geojson = fetch_geojson(where)
    geojson = normalize_fields(geojson, code_field, name_field)

    found_codes = sorted({f["properties"].get("KDPPUM") for f in geojson["features"]})
    print(f"Provinsi ditemukan: {found_codes} ({len(geojson['features'])} feature)")
    missing = set(KALIMANTAN_CODES) - set(found_codes)
    if missing:
        print(f"PERINGATAN: kode provinsi berikut TIDAK ditemukan: {sorted(missing)}")
        print("Cek ulang nama field / nilai kode di respons metadata sebelum lanjut.")
        sys.exit(1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(geojson, ensure_ascii=False), encoding="utf-8")
    print(f"Tersimpan: {OUTPUT_PATH.resolve()} ({OUTPUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()