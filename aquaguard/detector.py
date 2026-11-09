import numpy as np
import pandas as pd

def detect_anomalies(df: pd.DataFrame, window: int=96, k: float=4.0, min_excess: float=8.0) -> pd.DataFrame:
    """Per-meter high-side anomaly screening using a shifted rolling median and MAD."""
    out=df.copy()
    out["expected_l"]=np.nan
    out["robust_scale_l"]=np.nan
    for meter,idx in out.groupby("meter_id").groups.items():
        s=out.loc[idx,"volume_l"].astype(float)
        baseline=s.shift(1).rolling(window=window,min_periods=max(12,window//4)).median()
        abs_dev=(s-baseline).abs()
        mad=abs_dev.shift(1).rolling(window=window,min_periods=max(12,window//4)).median()
        scale=(1.4826*mad).clip(lower=1.0)
        out.loc[idx,"expected_l"]=baseline.to_numpy()
        out.loc[idx,"robust_scale_l"]=scale.to_numpy()
    out["excess_l"]=(out["volume_l"]-out["expected_l"]).clip(lower=0)
    out["is_anomaly"]=(out["expected_l"].notna() & (out["volume_l"]>out["expected_l"]+k*out["robust_scale_l"]) & (out["excess_l"]>=min_excess))
    out["reason"]=np.where(out["is_anomaly"],
        "Observed use is above this meter's recent rolling median by more than the robust variability threshold.",
        "")
    return out

def group_events(result: pd.DataFrame, max_gap_minutes: int=30):
    flagged=result[result["is_anomaly"]].copy()
    if flagged.empty: return []
    events=[]
    for meter,g in flagged.groupby("meter_id"):
        g=g.sort_values("timestamp")
        group_id=(g["timestamp"].diff().dt.total_seconds().div(60).fillna(0)>max_gap_minutes).cumsum()
        for _,event in g.groupby(group_id):
            events.append({
                "meter_id":meter,
                "start":event.timestamp.min(),
                "end":event.timestamp.max(),
                "flagged_readings":len(event),
                "estimated_excess_l":round(float(event.excess_l.sum()),1),
                "priority":"High" if len(event)>=8 or event.excess_l.sum()>=250 else "Review",
                "explanation":"Persistent readings above the meter's recent baseline"
            })
    return sorted(events,key=lambda x:x["estimated_excess_l"],reverse=True)
