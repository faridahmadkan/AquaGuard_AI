import numpy as np
import pandas as pd

def generate_demo_data(seed: int = 42) -> pd.DataFrame:
    """Five virtual meters, 28 days, 15-minute intervals, with reproducible injected events."""
    rng=np.random.default_rng(seed)
    times=pd.date_range("2026-10-01",periods=28*24*4,freq="15min")
    meters={
        "Academic Block": (18, 1.8, 7),
        "Laboratories": (24, 2.8, 11),
        "Residence Hall": (32, 3.2, 15),
        "Cafeteria": (20, 2.4, 9),
        "Landscaping": (12, 1.5, 5),
    }
    rows=[]
    for idx,(meter,(base,noise,peak)) in enumerate(meters.items()):
        for t_i,t in enumerate(times):
            hour=t.hour+t.minute/60
            weekday=t.dayofweek < 5
            # Synthetic operating profile: daytime demand with a lower overnight baseline.
            daytime=1.0 if 6 <= hour < 20 else 0.32
            if meter=="Residence Hall":
                daytime=0.75 if 0 <= hour < 6 else 1.15
            if meter=="Landscaping":
                daytime=1.3 if 5 <= hour < 9 else 0.12
            if not weekday and meter in ("Academic Block","Laboratories"):
                daytime*=0.58
            val=max(0.2,base*daytime+rng.normal(0,noise))
            injected=False
            # A multi-hour high-flow event for each of three meters.
            if meter=="Academic Block" and 9*24*4+40 <= t_i < 9*24*4+64:
                val+=42; injected=True
            if meter=="Residence Hall" and 17*24*4+20 <= t_i < 17*24*4+52:
                val+=35; injected=True
            if meter=="Cafeteria" and 23*24*4+12 <= t_i < 23*24*4+28:
                val+=28; injected=True
            rows.append((t,meter,round(float(val),2),injected))
    return pd.DataFrame(rows,columns=["timestamp","meter_id","volume_l","is_injected_anomaly"])
