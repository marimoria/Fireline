"""Render a portable, deterministic data snapshot using our own HTML template."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def render_dashboard(grids,summary,geojson,out):
    columns=["grid_id","date","latitude","longitude","province_name","region_id","region_name",
        "detection_count","active_days_7d","detections_7d","frp_median_mw","frp_max_mw",
        "priority_score","priority_level","activity_points","persistence_points","intensity_points",
        "high_count","nominal_count","low_count","unknown_count","night_count",
        "nearest_school_km","nearest_school_name","last_seen_utc","quality_note","grid_x","grid_y"]
    frame=grids[columns].copy()
    for c in ["latitude","longitude"]: frame[c]=frame[c].round(5)
    for c in ["frp_median_mw","frp_max_mw","priority_score","activity_points","persistence_points","intensity_points","nearest_school_km"]:
        frame[c]=frame[c].round(4)
    frame["last_seen_utc"]=frame.last_seen_utc.dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    payload={"columns":columns,"rows":json.loads(frame.to_json(orient="values",force_ascii=False)),
             "summary":summary,"boundaries":geojson}
    encoded=json.dumps(payload,ensure_ascii=False,separators=(",",":"),default=int).replace("<","\\u003c")
    template=(ROOT/"web"/"dashboard.html").read_text(encoding="utf-8")
    html=template.replace("__FIRELINE_DATA__",encoded)
    (out/"FIRELINE_Priority_Map.html").write_text(html,encoding="utf-8")
    (out/"dashboard_payload.json").write_text(encoded,encoding="utf-8")
    return html
