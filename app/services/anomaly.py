import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.05) -> pd.DataFrame:
    df = df.copy()
    if df.empty:
        df["is_anomaly"] = []
        return df

    model = IsolationForest(contamination=contamination, random_state=42)
    values = df[["amount"]].abs()
    scores = model.fit_predict(values)
    df["is_anomaly"] = scores == -1
    return df
