"""Inventory the Phase 1 kabupaten boundary and population inputs."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ADDITIONS = ROOT / "data" / "additions"


def fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geojson_inventory(path: Path) -> dict:
    gdf = gpd.read_file(path)
    props = [c for c in gdf.columns if c != "geometry"]
    province_values = sorted(gdf[props[0]].dropna().astype(str).unique().tolist()) if props else []
    return {
        "file": path.name,
        "type": "GeoJSON",
        "bytes": path.stat().st_size,
        "sha256": fingerprint(path),
        "features": len(gdf),
        "crs": str(gdf.crs),
        "geometry_types": sorted(gdf.geometry.geom_type.dropna().unique().tolist()),
        "invalid_geometries": int((~gdf.geometry.is_valid).sum()),
        "empty_geometries": int(gdf.geometry.is_empty.sum()),
        "columns": props,
        "first_property_values": province_values[:10],
    }


def delimited_inventory(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        rows = list(reader)
    return {
        "file": path.name,
        "type": "CSV",
        "bytes": path.stat().st_size,
        "sha256": fingerprint(path),
        "rows_including_header": len(rows),
        "columns": rows[0] if rows else [],
        "sample_rows": rows[1:4],
    }


def workbook_inventory(path: Path) -> dict:
    workbook = pd.ExcelFile(path)
    sheets = []
    for sheet in workbook.sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet, header=None)
        sheets.append({
            "sheet": sheet,
            "rows": int(frame.shape[0]),
            "columns": int(frame.shape[1]),
            "sample_rows": frame.iloc[:5].fillna("").astype(str).values.tolist(),
        })
    return {
        "file": path.name,
        "type": "XLSX",
        "bytes": path.stat().st_size,
        "sha256": fingerprint(path),
        "sheets": sheets,
    }


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    result = {"directory": str(ADDITIONS), "boundaries": [], "population": []}
    for path in sorted(ADDITIONS.glob("*.geojson")):
        result["boundaries"].append(geojson_inventory(path))
    for path in sorted(ADDITIONS.glob("*.csv")):
        result["population"].append(delimited_inventory(path))
    for path in sorted(ADDITIONS.glob("*.xlsx")):
        result["population"].append(workbook_inventory(path))
    output = ROOT / "review_outputs" / "phase1_data_inventory.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
