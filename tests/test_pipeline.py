import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box
from fireline.pipeline import rolling_days, percentile, score_features, assign_province, audit


def test_persistence_calendar_window_and_no_future():
    dates=["2024-08-01","2024-08-02","2024-08-07","2024-08-08","2024-08-20"]
    days,counts=rolling_days(dates,[20,3,4,7,9])
    assert list(days)==[1,2,3,3,1]
    assert list(counts)==[20,23,27,14,9]
    assert list(rolling_days(dates[:3],[20,3,4])[0])==list(days[:3])


def test_singleton_and_equal_values_do_not_become_max_priority():
    assert percentile(pd.Series([99])).iloc[0]==.5
    assert percentile(pd.Series([8,8,8])).tolist()==[.5,.5,.5]
    assert percentile(pd.Series([0,0])).tolist()==[0,0]


def test_score_breakdown_exact_and_ties_deterministic():
    d=pd.DataFrame({"date":["2024-08-01"]*2,"grid_id":["b","a"],
        "activity_component":[.5,.5],"persistence_component":[1/7,1/7],"intensity_component":[.5,.5]})
    result=score_features(d)
    assert result.grid_id.tolist()==["a","b"]
    assert np.allclose(result.priority_score,37.5)
    assert result.priority_level.tolist()==["P3","P3"]
    assert np.allclose(result.priority_score,result.activity_points+result.persistence_points+result.intensity_points)


def test_border_point_not_double_counted():
    g=gpd.GeoDataFrame({"province_code":["61","62"],"province_name":["A","B"]},geometry=[box(0,0,1,1),box(1,0,2,1)],crs=4326)
    result=assign_province(pd.DataFrame({"latitude":[.5,.5],"longitude":[1,3]}),g)
    assert len(result)==2
    assert result.iloc[0].province_code=="61"
    assert result.iloc[0].border_ambiguous
    assert pd.isna(result.iloc[1].province_code)


def test_invalid_hhmm_and_nonfinite_frp(tmp_path):
    boundaries=gpd.GeoDataFrame({"KDPPUM":["61","62","63","64","65"],"WADMPR":["A","B","C","D","E"]},geometry=[box(i,0,i+1,1) for i in range(5)],crs=4326)
    boundary=tmp_path/"b.geojson";boundaries.to_file(boundary,driver="GeoJSON")
    d=pd.DataFrame({"latitude":[.5]*5,"longitude":[.5]*5,"acq_date":["2024-08-01"]*5,
        "acq_time":[59,1260,2400,100.5,100],"frp":[np.inf,1,1,1,-5],"type":[0]*5,"confidence":["n"]*5,"daynight":["D"]*5})
    path=tmp_path/"f.csv";d.to_csv(path,index=False)
    raw,accepted,unmatched,invalid,g,stages=audit({"firms_csv":path,"provinces_geojson":boundary})
    assert len(invalid)==3
    assert len(accepted)==2
    assert accepted.frp.isna().all()
    assert stages.removed.sum()+len(accepted)==len(raw)
