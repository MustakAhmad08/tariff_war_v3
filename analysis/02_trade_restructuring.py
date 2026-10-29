"""Describe the restructuring of soybean trade with China, 2001-2024 (descriptive only)."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

d = pd.read_csv(ROOT / "data" / "processed" / "forest_loss.csv")
t = pd.DataFrame({
    "year": d["year"],
    "us_to_china_mt": d["Soy_Ex_US_CHINA (Kg)"] / 1e9,
    "brazil_to_china_mt": d["Soy_ex_BRA_CHINA (Kg)"] / 1e9,
    "brazil_total_exports_mt": d["Tot_Soy_Ex_BRA (Kg)"] / 1e9,
    "us_total_exports_mt": d["Tot_Soy_Ex_US (Kg)"] / 1e9,
})
t["china_share_of_brazil_exports_pct"] = 100 * t.brazil_to_china_mt / t.brazil_total_exports_mt
# Share of the two-supplier total only; other origins (e.g., Argentina) are not in the data.
t["brazil_share_of_us_brazil_supply_to_china_pct"] = (
    100 * t.brazil_to_china_mt / (t.brazil_to_china_mt + t.us_to_china_mt))
t.to_csv(OUT / "trade_restructuring_annual.csv", index=False)

periods = {"2015-2017": (2015, 2017), "2018": (2018, 2018), "2019-2024": (2019, 2024)}
rows = []
for name, (a, b) in periods.items():
    m = t[(t.year >= a) & (t.year <= b)].drop(columns="year").mean()
    rows.append({"period": name, **m.round(2).to_dict()})
p = pd.DataFrame(rows)
p.to_csv(OUT / "trade_restructuring_periods.csv", index=False)

y = t.set_index("year")
change = {
    "us_to_china_change_2017_2018_pct": 100 * (y.us_to_china_mt[2018] / y.us_to_china_mt[2017] - 1),
    "brazil_to_china_change_2017_2018_pct": 100 * (y.brazil_to_china_mt[2018] / y.brazil_to_china_mt[2017] - 1),
}
pd.Series(change).round(1).to_csv(OUT / "trade_restructuring_changes.csv", header=["value"])
print(p.to_string(index=False))
print(pd.Series(change).round(1).to_string())
