"""Create the single, presentation-ready table used by Power BI imports."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "review_outputs" / "grid_day_priority.csv"
TARGET = ROOT / "review_outputs" / "FIRELINE_PowerBI_AreaDay.csv"


def export(source=SOURCE, target=TARGET):
    df = pd.read_csv(source)
    columns = {
        "grid_id": "area_grid_id",
        "date": "observation_date_utc",
        "latitude": "latitude",
        "longitude": "longitude",
        "province_name": "province",
        "region_name": "kabupaten_kota",
        "region_id": "kabupaten_kota_id",
        "detection_count": "satellite_observations",
        "active_days_7d": "active_days_last_7",
        "detections_7d": "observations_last_7",
        "frp_median_mw": "frp_median_mw",
        "frp_max_mw": "frp_max_mw",
        "high_count": "confidence_high_count",
        "nominal_count": "confidence_nominal_count",
        "low_count": "confidence_low_count",
        "unknown_count": "confidence_unknown_count",
        "night_count": "night_observations",
        "first_seen_utc": "first_seen_utc",
        "last_seen_utc": "last_seen_utc",
        "nearest_school_km": "nearest_school_distance_km",
        "nearest_school_name": "nearest_school_name",
        "activity_points": "activity_points",
        "persistence_points": "persistence_points",
        "intensity_points": "intensity_points",
        "priority_score": "priority_score",
        "priority_level": "priority_level",
        "daily_rank": "daily_rank",
        "window_days_available": "window_days_available",
        "quality_note": "quality_note",
    }
    missing = sorted(set(columns) - set(df))
    if missing:
        raise ValueError(f"Kolom area-hari hilang: {missing}")
    out = df[list(columns)].rename(columns=columns).copy()
    out["observation_date_utc"] = pd.to_datetime(out.observation_date_utc).dt.strftime("%Y-%m-%d")
    for col in ["first_seen_utc", "last_seen_utc"]:
        out[col] = pd.to_datetime(out[col], utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    out.to_csv(target, index=False, encoding="utf-8-sig")
    return target


if __name__ == "__main__":
    print(export())
