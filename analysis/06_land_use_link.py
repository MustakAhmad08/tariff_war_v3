"""Link soybean-area change to land use with the version 2 transition accounting.

Inputs are copied unchanged from the version 2 repository (data/derived/v2_land_use/;
see data/README.md). This script checks their identities and builds the v3 tables.
The main reporting period is 2019-2024, the post-period of the BSTS model; 2018 and
2018-2024 are also written to land_use_by_period.csv.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V2 = ROOT / "data" / "derived" / "v2_land_use"
OUT = ROOT / "results" / "tables"
MAIN = "2019-2024"

acct = pd.read_csv(V2 / "Table_2_period_accounting.csv", dtype={"period": str}).set_index("period")
origins = pd.read_csv(V2 / "Table_3_soybean_entry_origins.csv")
hist = pd.read_csv(V2 / "Table_6_national_entry_histories.csv")
annual = pd.read_csv(V2 / "annual_soy_gain_origins_national.csv")
sa = pd.read_csv(V2 / "state_annual_areas.csv")
sa = sa[sa.run_mode == "national"]

# Identities: entry - exit = net change; origins sum to entry; entry groups sum to all.
assert (acct.gross_entry_ha - acct.soybean_exit_ha - acct.net_change_ha).abs().max() < 1e-3
assert abs(origins.gross_gain_ha.sum() - acct.loc["2018-2024", "gross_entry_ha"]) < 1
h = hist.set_index("population")
assert abs(h.loc[["first", "reentry", "unresolved"], "entry_ha"].sum() - h.loc["all", "entry_ha"]) < 1e-3
assert (annual.origin_sum - annual.all_new_soy).abs().max() < 1e-3
# The state-year accounting reproduces the national tables.
tot = sa[sa.year.between(2018, 2024)].sum(numeric_only=True)
assert abs(tot.all_entry_ha - h.loc["all", "entry_ha"]) < 1
assert abs(tot.all_native_w5_ha - h.loc["all", "native_w5_ha"]) < 1
for p, (lo, hi) in (("2018", (2018, 2018)), ("2019-2024", (2019, 2024))):
    e = sa[sa.year.between(lo, hi)].all_entry_ha.sum()
    assert abs(e - acct.loc[p, "gross_entry_ha"]) / e < 1e-5, p

ORIGINS = {"other_agriculture": "managed", "pasture": "managed", "mosaic": "managed",
           "woody": "native", "nonwoody": "native",
           "plantation": "other", "nonvegetated": "other", "water": "other"}
PERIODS = {"2018": (2018, 2018), "2019-2024": (2019, 2024), "2018-2024": (2018, 2024)}

# Shares by period on explicit denominators. Origin shares divide by gross entry (summed pixel-year
# entry events); history shares divide by entry with five valid prior maps. The native-history
# windows are nested (t-1 is inside t-1..t-5), so w5 - w1 is entry whose native cover was mapped two
# to five years earlier but not in the year before entry. Its class in t-1 was managed land except
# for at most the non-managed, non-native origin share, which gives a lower bound for
# native -> managed -> soybean.
rows, orig_rows = [], []
for label, (lo, hi) in PERIODS.items():
    d = sa[sa.year.between(lo, hi)].sum(numeric_only=True)
    for g in ("all", "first", "reentry"):
        e, el = d[f"{g}_entry_ha"], d[f"{g}_eligible5_ha"]
        by = {k: d[f"{g}_origin_{k}_ha"] for k in ORIGINS}
        grp = {c: sum(v for k, v in by.items() if ORIGINS[k] == c) for c in ("managed", "native", "other")}
        earlier = d[f"{g}_native_w5_ha"] - d[f"{g}_native_w1_ha"]
        rows.append({
            "period": label, "population": g, "entry_mha": e / 1e6, "eligible5_mha": el / 1e6,
            "entry_share_pct": 100 * e / d["all_entry_ha"],
            "prior_managed_pct": 100 * grp["managed"] / e, "prior_native_pct": 100 * grp["native"] / e,
            "prior_other_pct": 100 * grp["other"] / e,
            "native_w1_pct": 100 * d[f"{g}_native_w1_ha"] / el, "native_w3_pct": 100 * d[f"{g}_native_w3_ha"] / el,
            "native_w5_pct": 100 * d[f"{g}_native_w5_ha"] / el,
            "native_w5_woody_pct": 100 * d[f"{g}_woody_w5_ha"] / el,
            "native_w5_nonwoody_pct": 100 * d[f"{g}_nonwoody_w5_ha"] / el,
            "native_earlier_only_pct": 100 * earlier / el, "native_earlier_only_mha": earlier / 1e6,
            "native_then_managed_min_pct": max(0.0, 100 * (earlier - grp["other"]) / el),
            "native_w5_mha": d[f"{g}_native_w5_ha"] / 1e6,
        })
        if g == "all":
            orig_rows += [{"period": label, "origin": k, "group": ORIGINS[k], "entry_ha": v, "share_pct": 100 * v / e}
                          for k, v in by.items()]
period = pd.DataFrame(rows).round(3)
period.to_csv(OUT / "land_use_by_period.csv", index=False)
pd.DataFrame(orig_rows).round(3).to_csv(OUT / "soybean_entry_origins_by_period.csv", index=False)

m = period[period.period == MAIN].set_index("population")
summary = pd.DataFrame([
    {"measure": "Gross soybean entry", "value": m.loc["all", "entry_mha"], "unit": "Mha"},
    {"measure": "Soybean exit", "value": acct.loc[MAIN, "soybean_exit_ha"] / 1e6, "unit": "Mha"},
    {"measure": "Net soybean-area change", "value": acct.loc[MAIN, "net_change_ha"] / 1e6, "unit": "Mha"},
    {"measure": "Re-entry share of entry", "value": m.loc["reentry", "entry_share_pct"], "unit": "%"},
    {"measure": "First observed entry share of entry", "value": m.loc["first", "entry_share_pct"], "unit": "%"},
    {"measure": "Managed land immediately before entry", "value": m.loc["all", "prior_managed_pct"], "unit": "%"},
    {"measure": "Native cover immediately before entry", "value": m.loc["all", "prior_native_pct"], "unit": "%"},
    {"measure": "Native cover within 1 year, all entry", "value": m.loc["all", "native_w1_pct"], "unit": "%"},
    {"measure": "Native cover within 3 years, all entry", "value": m.loc["all", "native_w3_pct"], "unit": "%"},
    {"measure": "Native cover within 5 years, all entry", "value": m.loc["all", "native_w5_pct"], "unit": "%"},
    {"measure": "Native cover within 5 years, first observed entry", "value": m.loc["first", "native_w5_pct"], "unit": "%"},
    {"measure": "Native cover within 5 years, re-entry", "value": m.loc["reentry", "native_w5_pct"], "unit": "%"},
    {"measure": "Entry with native cover within 5 years", "value": m.loc["all", "native_w5_mha"], "unit": "Mha"},
])
summary["period"] = MAIN
summary["value"] = summary["value"].round(3)
summary.to_csv(OUT / "land_use_link_summary.csv", index=False)

m.reset_index()[["population", "entry_mha", "entry_share_pct", "native_w1_pct", "native_w3_pct",
                 "native_w5_pct", "native_w5_mha"]].to_csv(OUT / "native_history_by_entry_group.csv", index=False)
print(period.to_string(index=False))
print(summary.to_string(index=False))
