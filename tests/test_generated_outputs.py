"""Integration checks on the locally built snapshot; skipped until build exists."""
import json
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "review_outputs"
pytestmark = pytest.mark.skipif(not (OUT / "grid_day_priority.csv").exists(), reason="Build local snapshot first")


def test_snapshot_conservation_and_keys():
    summary = json.loads((OUT / "audit_summary.json").read_text(encoding="utf-8"))
    grids = pd.read_csv(OUT / "grid_day_priority.csv")
    assert sum(s["removed"] for s in summary["stage_counts"]) + summary["kalimantan_observations"] == summary["raw_rows"]
    assert len(grids) == summary["grid_day_rows"]
    assert not grids.duplicated(["grid_id", "date"]).any()
    assert grids.detection_count.sum() == summary["kalimantan_observations"]
    assert grids.active_days_7d.between(1, 7).all()
    assert grids.priority_score.between(0, 100).all()
    assert np.allclose(grids.priority_score, grids.activity_points + grids.persistence_points + grids.intensity_points, atol=.000051)
    assert (grids.high_count + grids.nominal_count + grids.low_count + grids.unknown_count).equals(grids.detection_count)


def test_rolling_matches_independent_calendar_calculation():
    grids = pd.read_csv(OUT / "grid_day_priority.csv")
    # All grids, all dates. Independent date-set reference, no vectorized rolling helper.
    for _, group in grids.groupby("grid_id"):
        dates = [d.date() for d in pd.to_datetime(group.date)]
        for row, day in zip(group.itertuples(), dates):
            keep = np.array([day-timedelta(days=6) <= candidate <= day for candidate in dates])
            assert row.active_days_7d == int(keep.sum())
            assert row.detections_7d == group.loc[keep, "detection_count"].sum()


def test_payload_matches_rank_and_html_is_escaped():
    payload = json.loads((OUT / "dashboard_payload.json").read_text(encoding="utf-8"))
    frame = pd.DataFrame(payload["rows"], columns=payload["columns"])
    grids = pd.read_csv(OUT / "grid_day_priority.csv")
    ordered = frame.sort_values(["date", "priority_score", "grid_id"], ascending=[True, False, True])
    assert ordered[["grid_id", "date"]].values.tolist() == grids[["grid_id", "date"]].values.tolist()
    assert set(frame.priority_level) <= {"P1", "P2", "P3"}
    assert "<" not in (OUT / "dashboard_payload.json").read_text(encoding="utf-8")
    assert "__FIRELINE_DATA__" not in (OUT / "FIRELINE_Priority_Map.html").read_text(encoding="utf-8")


def test_notebooks_completed_without_errors():
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        nb = json.loads(path.read_text(encoding="utf-8"))
        code = [c for c in nb["cells"] if c["cell_type"] == "code"]
        assert code
        assert all(c["execution_count"] is not None for c in code)
        assert not any(o.get("output_type") == "error" for c in code for o in c["outputs"])


def test_streamlit_shell_renders_without_exception():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(str(ROOT / "dashboard.py")).run(timeout=30)
    assert not app.exception
