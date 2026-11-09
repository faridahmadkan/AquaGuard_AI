import pandas as pd

REQUIRED={"timestamp","meter_id","volume_l"}

def validate_readings(df: pd.DataFrame):
    missing=REQUIRED-set(df.columns)
    if missing:
        raise ValueError("Missing required columns: "+", ".join(sorted(missing)))
    out=df.copy()
    notes=[]
    out["timestamp"]=pd.to_datetime(out["timestamp"],errors="coerce")
    out["volume_l"]=pd.to_numeric(out["volume_l"],errors="coerce")
    before=len(out)
    out=out.dropna(subset=["timestamp","meter_id","volume_l"])
    if len(out)<before: notes.append(f"Removed {before-len(out)} rows with invalid or missing values")
    out["meter_id"]=out["meter_id"].astype(str).str.strip()
    out=out[(out["meter_id"]!="") & (out["volume_l"]>=0)]
    if len(out)<before and "Removed" not in " ".join(notes): notes.append("Removed blank meter IDs or negative volumes")
    duplicates=int(out.duplicated(["timestamp","meter_id"]).sum())
    if duplicates:
        out=out.drop_duplicates(["timestamp","meter_id"],keep="last")
        notes.append(f"Removed {duplicates} duplicate meter/timestamp rows")
    out=out.sort_values(["meter_id","timestamp"]).reset_index(drop=True)
    if out.empty: raise ValueError("No valid readings remain after validation")
    return out,notes
