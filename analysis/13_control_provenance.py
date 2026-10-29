"""Provenance of the climate controls in forest_loss.csv.

The compiled workbook labels the model's climate columns (hum, prec, temp) as taken from the World
Bank Climate Change Knowledge Portal. They are much smoother than the annual CRU TS 4.09 national
means for Brazil from that portal. This script compares them with the raw annual series and with
one-sided (trailing moving average, one-sided Hodrick-Prescott) and two-sided (centered moving
average, Hodrick-Prescott) smoothers. A close match to a two-sided smoother means that each stored
value uses later years. The raw annual CRU series is cached in data/processed/; the baseline
specification uses it in place of the stored climate series (analysis/01).
"""
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data" / "processed"
OUT = ROOT / "results" / "tables"
CRU = {"temp": "tas", "prec": "pr", "hum": "hurs"}
HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

cru_file = P / "cru_ts409_brazil_annual.csv"
if not cru_file.exists():
    cols = {}
    for name, var in CRU.items():
        url = (f"https://cckpapi.worldbank.org/cckp/v1/cru-x0.5_timeseries_{var}_timeseries_annual_"
               f"1901-2024_mean_historical_cru_ts4.09_mean/BRA?_format=json")
        j = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60).read())
        cols[name] = {int(k[:4]): v for k, v in j["data"]["BRA"].items()}
    pd.DataFrame(cols).sort_index().rename_axis("year").to_csv(cru_file)

d = pd.read_csv(P / "forest_loss.csv").set_index("year")
cru = pd.read_csv(cru_file).set_index("year")


def hp(y, lam):
    n = len(y)
    D = np.diff(np.eye(n), 2, axis=0)
    return np.linalg.solve(np.eye(n) + lam * D.T @ D, y)


rows = []
for col in CRU:
    x, s = d[col], cru[col]
    cands = {"raw annual": ("none", s)}
    for w in range(2, 11):
        cands[f"trailing moving average, {w} years"] = ("one-sided", s.rolling(w).mean())
        cands[f"centered moving average, {w} years"] = ("two-sided", s.rolling(w, center=True).mean())
    for lam in (1, 3, 10, 30, 100, 300, 1000):
        z = s.loc[2001:2024]
        cands[f"Hodrick-Prescott 2001-2024, lambda {lam}"] = ("two-sided", pd.Series(hp(z.values, lam), index=z.index))
        cands[f"one-sided Hodrick-Prescott from 2001, lambda {lam}"] = (
            "one-sided", pd.Series({t: hp(s.loc[2001:t].values, lam)[-1] for t in x.index if t >= 2006}))
    for name, (kind, f) in cands.items():
        f = f.reindex(x.index)
        ok = f.notna()
        rows.append({"control": col, "comparison": name, "kind": kind,
                     "rmse": float(np.sqrt(((x[ok] - f[ok]) ** 2).mean())), "years": int(ok.sum())})
out = pd.DataFrame(rows)
out.to_csv(OUT / "climate_provenance.csv", index=False)
best = out.loc[out.groupby(["control", "kind"]).rmse.idxmin()]
print(best.to_string(index=False))
