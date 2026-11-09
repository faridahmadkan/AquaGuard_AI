import pandas as pd
from aquaguard.data import generate_demo_data
from aquaguard.validation import validate_readings
from aquaguard.detector import detect_anomalies, group_events
from aquaguard.simulator import simulate_savings
from aquaguard.evaluation import evaluate_detection
from aquaguard.forecast import forecast_seven_days

def test_demo_shape():
    df=generate_demo_data()
    assert len(df)==5*28*24*4
    assert df.meter_id.nunique()==5

def test_validation_deduplicates():
    df=pd.DataFrame({"timestamp":["2026-01-01","2026-01-01"],"meter_id":["A","A"],"volume_l":[2,3]})
    out,notes=validate_readings(df)
    assert len(out)==1 and out.volume_l.iloc[0]==3

def test_simulator_example():
    r=simulate_savings(25,48,8)
    assert r["current_loss_l"]==1200
    assert r["target_loss_l"]==200
    assert r["avoided_l"]==1000

def test_evaluation():
    m=evaluate_detection([1,1,0,0],[1,0,1,0])
    assert (m["TP"],m["FP"],m["FN"],m["TN"])==(1,1,1,1)

def test_forecast():
    df=generate_demo_data().drop(columns=["is_injected_anomaly"])
    assert len(forecast_seven_days(df))==7
