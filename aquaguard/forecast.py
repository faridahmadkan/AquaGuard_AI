import pandas as pd

def daily_totals(df):
    return df.assign(date=pd.to_datetime(df.timestamp).dt.normalize()).groupby("date").volume_l.sum().sort_index()

def forecast_seven_days(df):
    daily=daily_totals(df)
    if len(daily)<7: raise ValueError("At least seven complete days of data are needed for forecasting")
    rows=[]
    history=daily.copy()
    for _ in range(7):
        next_date=history.index.max()+pd.Timedelta(days=1)
        same=history[history.index.dayofweek==next_date.dayofweek].tail(4)
        weekday_median=float(same.median()) if len(same) else float(history.tail(7).median())
        recent_median=float(history.tail(14).median())
        pred=max(0,0.7*weekday_median+0.3*recent_median)
        rows.append({"date":next_date.date(),"forecast_l":round(pred,1)})
        history.loc[next_date]=pred
    return pd.DataFrame(rows)

def forecast_mae(df):
    daily=daily_totals(df)
    if len(daily)<15: return float("nan")
    errors=[]
    # Rolling-origin one-day-ahead holdout using only data before each target day.
    for i in range(max(7,len(daily)-7),len(daily)):
        hist=daily.iloc[:i]
        target=daily.index[i]
        same=hist[hist.index.dayofweek==target.dayofweek].tail(4)
        pred=0.7*float(same.median())+0.3*float(hist.tail(14).median())
        errors.append(abs(float(daily.iloc[i])-pred))
    return sum(errors)/len(errors) if errors else float("nan")
