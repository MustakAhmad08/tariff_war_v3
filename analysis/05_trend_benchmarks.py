"""Simple pre-2018 trend benchmarks for soybean area (MapBiomas and IBGE).

These are transparent reference points for the BSTS results, not causal estimates.
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"

d = pd.read_csv(ROOT / "data" / "processed" / "forest_loss.csv").set_index("year")
ibge = pd.read_csv(ROOT / "data" / "processed" / "ibge_soy_planted_area_brazil.csv").set_index("year")
series = {"MapBiomas soybean area": d["FCL_Soybean"], "IBGE planted area": ibge["ibge_planted_soy_ha"]}

rows = []
for name, s in series.items():
    for a, b in [(2002, 2018), (2008, 2018), (2012, 2018), (2014, 2018)]:
        x = np.arange(a, b + 1)
        slope, intercept = np.polyfit(x, s.loc[a:b].to_numpy(), 1)
        post = np.arange(2019, 2025)
        pred = slope * post + intercept
        obs = s.loc[2019:2024].to_numpy()
        rows.append({"series": name, "trend_window": f"{a}-{b}", "slope_mha_per_year": slope / 1e6,
                     "observed_mean_mha": obs.mean() / 1e6, "trend_mean_mha": pred.mean() / 1e6,
                     "difference_mha": (obs - pred).mean() / 1e6})
    rows.append({"series": name, "trend_window": "flat at 2018", "slope_mha_per_year": 0.0,
                 "observed_mean_mha": s.loc[2019:2024].mean() / 1e6, "trend_mean_mha": s[2018] / 1e6,
                 "difference_mha": (s.loc[2019:2024].mean() - s[2018]) / 1e6})
out = pd.DataFrame(rows).round(3)
out.to_csv(OUT / "trend_benchmarks.csv", index=False)

growth = []
for name, s in series.items():
    for a, b in [(2002, 2018), (2012, 2018), (2018, 2024)]:
        growth.append({"series": name, "period": f"{a}-{b}", "start_mha": s[a] / 1e6, "end_mha": s[b] / 1e6,
                       "mean_annual_growth_mha": (s[b] - s[a]) / (b - a) / 1e6})
g = pd.DataFrame(growth).round(3)
g.to_csv(OUT / "soybean_area_growth.csv", index=False)
print(out.to_string(index=False)); print(g.to_string(index=False))
