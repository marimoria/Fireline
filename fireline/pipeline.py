"""Deterministic analysis. No network calls; read-only inputs, explicit output folder."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = {"activity": 0.40, "persistence": 0.35, "intensity": 0.25}
VERSION = "priority-map-1.0"


def settings(path=None):
    path = Path(path) if path else ROOT / "config.local.json"
    if not path.exists():
        raise FileNotFoundError("Salin config.example.json menjadi config.local.json dan isi lokasi dataset.")
    config = json.loads(path.read_text(encoding="utf-8"))
    for key in ("firms_csv", "provinces_geojson", "schools_csv", "kaka_html"):
        value = config.get(key)
        config[key] = (path.parent / value).resolve() if value else None
    if not 0 < config.get("grid_degrees", 0.1) <= 1:
        raise ValueError("grid_degrees harus > 0 dan <= 1.")
    return config


def fingerprint(path):
    return {"file": path.name, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def province_boundaries(path):
    g = gpd.read_file(path).to_crs(4326).rename(columns={"KDPPUM": "province_code", "WADMPR": "province_name"})
    g["province_code"] = g.province_code.astype(str)
    g = g[g.province_code.isin(["61", "62", "63", "64", "65"])].copy()
    if set(g.province_code) != {"61", "62", "63", "64", "65"}:
        raise ValueError("Boundary wajib mencakup kelima provinsi Kalimantan.")
    g.geometry = g.geometry.make_valid()
    return g[["province_code", "province_name", "geometry"]]


def assign_province(df, boundaries, lat="latitude", lon="longitude"):
    points = gpd.GeoDataFrame(df.copy(), geometry=gpd.points_from_xy(df[lon], df[lat]), crs=4326)
    joined = gpd.sjoin(points, boundaries, how="left", predicate="intersects")
    # A point exactly on a shared border may match two polygons. Keep deterministic
    # attribution and mark ambiguity; never duplicate a detection in downstream totals.
    multiple = joined.groupby(level=0).province_code.count().gt(1)
    joined = joined.sort_values("province_code").loc[lambda d: ~d.index.duplicated()]
    joined["border_ambiguous"] = joined.index.map(multiple).fillna(False)
    return pd.DataFrame(joined.drop(columns=["geometry", "index_right"])).sort_index()


def audit(config):
    raw = pd.read_csv(config["firms_csv"])
    required = {"latitude", "longitude", "acq_date", "acq_time", "frp", "type", "confidence", "daynight"}
    if required - set(raw.columns):
        raise ValueError(f"Kolom FIRMS belum lengkap: {sorted(required-set(raw.columns))}")
    raw["source_row"] = np.arange(len(raw))
    count = [{"stage": "Mentah", "retained": len(raw), "removed": 0}]
    df = raw.drop_duplicates(subset=list(raw.columns.drop("source_row"))).copy()
    count.append({"stage": "Duplikat persis dihapus", "retained": len(df), "removed": len(raw)-len(df)})
    for col in ["latitude", "longitude", "frp", "type"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    times = pd.to_numeric(df.acq_time, errors="coerce")
    valid_time = times.notna() & times.eq(np.floor(times)) & times.between(0,2359) & times.mod(100).lt(60)
    safe_time = times.where(valid_time, 0).astype(int).astype(str).str.zfill(4)
    df["observed_at_utc"] = pd.to_datetime(df.acq_date.astype(str)+" "+safe_time, format="%Y-%m-%d %H%M", errors="coerce", utc=True)
    good = valid_time & df.observed_at_utc.notna() & df.latitude.between(-90,90) & df.longitude.between(-180,180)
    before = len(df); invalid = df.loc[~good].copy(); df = df.loc[good].copy()
    count.append({"stage": "Koordinat dan waktu valid", "retained": len(df), "removed": before-len(df)})
    before = len(df); df = df.loc[df.type.eq(0)].copy()
    count.append({"stage": "Type 0 (dugaan api vegetasi)", "retained": len(df), "removed": before-len(df)})
    boundaries = province_boundaries(config["provinces_geojson"])
    joined = assign_province(df, boundaries)
    unmatched = joined.loc[joined.province_code.isna()].copy()
    accepted = joined.loc[joined.province_code.notna()].copy()
    count.append({"stage": "Di dalam poligon BIG Kalimantan", "retained": len(accepted), "removed": len(unmatched)})
    # Invalid FRP stays as missing evidence; never silently replace it with a valid zero.
    accepted.loc[~np.isfinite(accepted.frp) | accepted.frp.lt(0), "frp"] = np.nan
    accepted["date"] = accepted.observed_at_utc.dt.strftime("%Y-%m-%d")
    accepted["confidence"] = accepted.confidence.astype(str).str.lower().where(lambda s:s.isin(["l","n","h"]), "unknown")
    accepted["daynight"] = accepted.daynight.astype(str).str.upper()
    return raw, accepted, unmatched, invalid, boundaries, pd.DataFrame(count)


def rolling_days(dates, counts, days=7):
    """Past and current calendar days only. An observation gap is not sensor coverage."""
    index = np.asarray(pd.to_datetime(dates), dtype="datetime64[D]")
    counts = np.asarray(counts)
    left = np.searchsorted(index, index - np.timedelta64(days-1, "D"), side="left")
    running = np.r_[0, counts.cumsum()]
    return np.arange(len(index))+1-left, running[np.arange(len(index))+1]-running[left]


def percentile(series):
    # Mid-rank: one active area / all tied areas receive 0.5, not artificial 100%.
    ranks = (series.rank(method="average")-0.5) / series.notna().sum() if series.notna().any() else series*np.nan
    return ranks.where(series.ne(0), 0).fillna(0)


def score_features(df, weights=WEIGHTS):
    if any(v < 0 for v in weights.values()) or not np.isclose(sum(weights.values()), 1):
        raise ValueError("Bobot non-negatif dan jumlahnya harus 1.")
    result = df.copy()
    for component, weight in weights.items():
        result[f"{component}_points"] = result[f"{component}_component"] * 100 * weight
    result["priority_score"] = result[[f"{c}_points" for c in weights]].sum(axis=1).round(4)
    result["priority_level"] = np.select([result.priority_score.ge(80), result.priority_score.ge(60)], ["P1", "P2"], default="P3")
    result = result.sort_values(["date","priority_score","grid_id"], ascending=[True,False,True])
    result["daily_rank"] = result.groupby("date").cumcount()+1
    return result.reset_index(drop=True)


def make_grid_days(accepted, boundaries, config):
    df = accepted.copy()
    step = config.get("grid_degrees",0.1)
    df["grid_y"] = np.floor(df.latitude / step + 1e-9).astype(int)
    df["grid_x"] = np.floor(df.longitude / step + 1e-9).astype(int)
    df["grid_id"] = df.grid_y.astype(str)+":"+df.grid_x.astype(str)
    df["high"] = df.confidence.eq("h").astype(int)
    df["nominal"] = df.confidence.eq("n").astype(int)
    df["low"] = df.confidence.eq("l").astype(int)
    df["unknown"] = df.confidence.eq("unknown").astype(int)
    df["night"] = df.daynight.eq("N").astype(int)
    grouped = df.groupby(["grid_id","date"], sort=True)
    grids = grouped.agg(detection_count=("source_row","size"),frp_median_mw=("frp","median"),frp_max_mw=("frp","max"),
        frp_missing=("frp",lambda s:s.isna().sum()), high_count=("high","sum"),nominal_count=("nominal","sum"),
        low_count=("low","sum"),unknown_count=("unknown","sum"),night_count=("night","sum"),
        first_seen_utc=("observed_at_utc","min"),last_seen_utc=("observed_at_utc","max"),
        province_count=("province_code","nunique")).reset_index()
    # Display a real observed coordinate with maximum FRP, not an invented ignition
    # point or the centre of an 11 km square. Ties use latest time, then source row.
    representatives = df.sort_values(["frp","observed_at_utc","source_row"],ascending=[False,False,True],na_position="last").drop_duplicates(["grid_id","date"])
    cols=["grid_id","date","grid_x","grid_y","latitude","longitude","province_code","province_name","source_row"]
    grids=grids.merge(representatives[cols],on=["grid_id","date"],validate="one_to_one")
    grids["active_days_7d"]=0; grids["detections_7d"]=0
    for _, sub in grids.sort_values("date").groupby("grid_id"):
        active, total=rolling_days(sub.date,sub.detection_count)
        grids.loc[sub.index,"active_days_7d"]=active
        grids.loc[sub.index,"detections_7d"]=total
    start=pd.Timestamp(accepted.date.min())
    grids["window_days_available"]=(pd.to_datetime(grids.date)-start).dt.days.add(1).clip(upper=7)
    grids["activity_component"]=grids.groupby("date").detection_count.transform(percentile)
    grids["intensity_component"]=grids.groupby("date").frp_median_mw.transform(percentile)
    grids["persistence_component"]=grids.active_days_7d / 7
    grids["nearest_school_km"]=np.nan
    grids["nearest_school_name"]="Tidak tersedia"
    schools_count=0
    if config.get("schools_csv") and config["schools_csv"].exists():
        schools=pd.read_csv(config["schools_csv"],low_memory=False)
        schools["lat"]=pd.to_numeric(schools.lat,errors="coerce")
        schools["long"]=pd.to_numeric(schools.long,errors="coerce")
        schools=schools.loc[schools.lat.between(-5,5) & schools.long.between(108,120)].drop_duplicates(["lat","long","school_name"])
        schools=assign_province(schools.drop(columns=["province_name"]).reset_index(drop=True),boundaries,"lat","long")
        schools=schools.loc[schools.province_code.notna()].reset_index(drop=True)
        schools_count=len(schools)
        if schools_count:
            tree=BallTree(np.radians(schools[["lat","long"]]),metric="haversine")
            distance, indices=tree.query(np.radians(grids[["latitude","longitude"]]),k=1)
            grids["nearest_school_km"]=distance[:,0]*6371.0088
            grids["nearest_school_name"]=schools.iloc[indices[:,0]].school_name.fillna("Nama tidak tersedia").to_numpy()
    grids["quality_note"]=grids.apply(lambda r:"; ".join(filter(None,[
        "Jendela awal kurang dari 7 hari" if r.window_days_available<7 else "",
        "Ada FRP tidak valid/kosong" if r.frp_missing else "",
        "Ada confidence tidak dikenal" if r.unknown_count else "",
        "Grid melintasi provinsi; label mengikuti titik representatif" if r.province_count>1 else "",
        "Konteks sekolah tidak tersedia" if pd.isna(r.nearest_school_km) else ""
    ])) or "Tidak ada catatan audit tambahan",axis=1)
    return score_features(grids), schools_count


def sensitivity(grids):
    variants={"equal_three":dict(activity=1/3,persistence=1/3,intensity=1/3),
        "activity_heavy":dict(activity=.55,persistence=.25,intensity=.20),
        "persistence_heavy":dict(activity=.25,persistence=.55,intensity=.20),
        "without_activity":dict(activity=0,persistence=.35/.60,intensity=.25/.60),
        "without_persistence":dict(activity=.40/.65,persistence=0,intensity=.25/.65),
        "without_intensity":dict(activity=.40/.75,persistence=.35/.75,intensity=0)}
    rows=[]
    baseline={d:set(g.head(10).grid_id) for d,g in grids.groupby("date")}
    informative={d for d,g in grids.groupby("date") if len(g)>10}
    for name,w in variants.items():
        alt=score_features(grids,w)
        j=[]
        for d,g in alt.groupby("date"):
            if d not in informative: continue
            a,b=baseline[d],set(g.head(10).grid_id)
            j.append(len(a&b)/len(a|b))
        rows.append({"variant":name,"weights":w,"days_with_more_than_10_areas":len(j),
                     "mean_top10_jaccard":round(float(np.mean(j)),4) if j else None,
                     "min_top10_jaccard":round(float(np.min(j)),4) if j else None})
    return rows


def visual_boundaries(config, provinces):
    if config.get("kaka_html") and config["kaka_html"].exists():
        html=config["kaka_html"].read_text(encoding="utf-8")
        match=re.search(r"geo_json_\w+_add\((\{.*\})\);",html)
        if match:
            feature_collection=json.loads(match.group(1))
            g=gpd.GeoDataFrame.from_features(feature_collection["features"],crs=4326)
            g.geometry=g.geometry.make_valid()
            # Strip all old scores/ranks/confidence: reuse geometry only.
            g=g[["kab_kota","provinsi","geometry"]].rename(columns={"kab_kota":"region_name","provinsi":"province_name"})
            return g, "Kab/kota dari HTML Kaka; sumber dan tahun boundary belum tercantum. Hanya konteks visual."
    g=provinces.copy();g["region_name"]=g.province_name
    return g[["region_name","province_name","geometry"]], "BIG, batas provinsi; tidak tersedia boundary kab/kota Kaka."


def build(config_path=None):
    config=settings(config_path)
    raw,accepted,unmatched,invalid,provinces,stages=audit(config)
    grids,schools_count=make_grid_days(accepted,provinces,config)
    regions,region_note=visual_boundaries(config,provinces)
    regions=regions.reset_index(drop=True);regions["region_id"]=regions.index.astype(str)
    pts=gpd.GeoDataFrame(grids.copy(),geometry=gpd.points_from_xy(grids.longitude,grids.latitude),crs=4326)
    mapped=gpd.sjoin(pts,regions[["region_id","region_name","geometry"]],how="left",predicate="intersects")
    mapped=mapped.sort_values("region_id").loc[lambda d:~d.index.duplicated()].sort_index()
    grids["region_id"]=mapped.region_id.fillna("").to_numpy()
    grids["region_name"]=mapped.region_name.fillna("Kab/kota belum terpetakan").to_numpy()
    # Simplification affects display only; original geometry used above for assignment.
    display_regions=regions.copy(); display_regions.geometry=display_regions.geometry.simplify(.003,preserve_topology=True)
    geojson=json.loads(display_regions.to_json(drop_id=True))
    generated=datetime.now(timezone.utc).isoformat(timespec="seconds")
    daily=accepted.groupby("date").size()
    provinces_count=accepted.province_name.value_counts().rename_axis("province").reset_index(name="observations")
    summary={"version":VERSION,"generated_at_utc":generated,"mode":"historical_prototype",
        "raw_rows":len(raw),"kalimantan_observations":len(accepted),"unmatched_polygon_rows":len(unmatched),
        "invalid_coordinate_time_rows":len(invalid),"grid_day_rows":len(grids),"unique_grids":grids.grid_id.nunique(),
        "date_start":accepted.date.min(),"date_end":accepted.date.max(),"demo_date":str(daily.idxmax()),
        "demo_observations":int(daily.max()),"schools_in_boundary":schools_count,"weights":WEIGHTS,
        "grid_degrees":config.get("grid_degrees",.1),"region_note":region_note,
        "boundary_count":len(provinces),"visual_boundary_count":len(regions),
        "frp_missing_observations":int(accepted.frp.isna().sum()),
        "confidence_counts":accepted.confidence.value_counts().to_dict(),
        "unmapped_representative_grid_days":int(grids.region_id.eq("").sum()),
        "median_representative_school_km":round(float(grids.nearest_school_km.median()),3) if grids.nearest_school_km.notna().any() else None,
        "stage_counts":stages.to_dict("records"),"province_counts":provinces_count.to_dict("records"),
        "sensitivity":sensitivity(grids),
        "sources":{k:fingerprint(config[k]) for k in ["firms_csv","provinces_geojson","schools_csv","kaka_html"] if config.get(k) and config[k].exists()}}
    out=ROOT/"review_outputs";out.mkdir(exist_ok=True)
    accepted.to_csv(out/"accepted_observations.csv",index=False)
    unmatched.to_csv(out/"unmatched_boundary.csv",index=False)
    invalid.to_csv(out/"invalid_coordinates_time.csv",index=False)
    grids.to_csv(out/"grid_day_priority.csv",index=False)
    stages.to_csv(out/"audit_stages.csv",index=False)
    (out/"audit_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=int),encoding="utf-8")
    from fireline.render import render_dashboard
    render_dashboard(grids,summary,geojson,out)
    return summary,grids


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--config");args=p.parse_args()
    summary,_=build(args.config)
    print(json.dumps(summary,ensure_ascii=False,indent=2,default=int))
