"""Every number cited in the manuscript, computed from results/tables.

Text uses «key» placeholders; fill() replaces them, and fails on an unknown key, so the
prose cannot drift from the analysis outputs.
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
T = ROOT / "results" / "tables"
V2 = ROOT / "data" / "derived" / "v2_land_use"

N = {}


def mha(x, d=2):
    return f"{x / 1e6:.{d}f}"


def signed(x, d=2):
    v = x / 1e6
    return f"{'+' if v > 0 else '−'}{abs(v):.{d}f}"


def ci(lo, hi, d=2):
    f = lambda v: f"{'−' if v < 0 else ''}{abs(v) / 1e6:.{d}f}"
    return f"{f(lo)} to {f(hi)}"


# Trade.
tr = pd.read_csv(T / "trade_restructuring_annual.csv").set_index("year")
tp = pd.read_csv(T / "trade_restructuring_periods.csv").set_index("period")
for y in (2017, 2018, 2024):
    N[f"us_cn_{y}"] = f"{tr.us_to_china_mt[y]:.1f}"
    N[f"br_cn_{y}"] = f"{tr.brazil_to_china_mt[y]:.1f}"
    N[f"cn_share_br_{y}"] = f"{tr.china_share_of_brazil_exports_pct[y]:.1f}"
    N[f"br_share_{y}"] = f"{tr.brazil_share_of_us_brazil_supply_to_china_pct[y]:.1f}"
N["us_cn_change_2018"] = f"{100 * (1 - tr.us_to_china_mt[2018] / tr.us_to_china_mt[2017]):.0f}"
N["br_cn_change_2018"] = f"{100 * (tr.brazil_to_china_mt[2018] / tr.brazil_to_china_mt[2017] - 1):.0f}"
for p, k in (("2015-2017", "pre"), ("2019-2024", "post")):
    N[f"br_cn_{k}"] = f"{tp.loc[p, 'brazil_to_china_mt']:.1f}"
    N[f"us_cn_{k}"] = f"{tp.loc[p, 'us_to_china_mt']:.1f}"
    N[f"br_share_{k}"] = f"{tp.loc[p, 'brazil_share_of_us_brazil_supply_to_china_pct']:.1f}"
    N[f"br_tot_{k}"] = f"{tp.loc[p, 'brazil_total_exports_mt']:.1f}"
    N[f"cn_share_br_{k}"] = f"{tp.loc[p, 'china_share_of_brazil_exports_pct']:.1f}"

# Soybean area.
fl = pd.read_csv(ROOT / "data" / "processed" / "forest_loss.csv").set_index("year")["FCL_Soybean"]
for y in (2001, 2017, 2018, 2024):
    N[f"area_{y}"] = mha(fl[y], 1)
N["area_post_mean"] = mha(fl.loc[2019:2024].mean(), 1)
g = pd.read_csv(T / "soybean_area_growth.csv").set_index(["series", "period"])
for s, k in (("MapBiomas soybean area", "mb"), ("IBGE planted area", "ibge")):
    for per in ("2012-2018", "2018-2024", "2002-2018"):
        N[f"growth_{k}_{per[:4]}_{per[-4:]}"] = f"{g.loc[(s, per), 'mean_annual_growth_mha']:.2f}"
    N[f"{k}_2018"] = f"{g.loc[(s, '2018-2024'), 'start_mha']:.1f}"
    N[f"{k}_2024"] = f"{g.loc[(s, '2018-2024'), 'end_mha']:.1f}"
tb = pd.read_csv(T / "trend_benchmarks.csv").set_index(["series", "trend_window"])
for w in ("2002-2018", "2012-2018", "2014-2018"):
    v = tb.loc[("MapBiomas soybean area", w), "difference_mha"]
    N[f"trend_diff_mb_{w[:4]}"] = f"{abs(v):.1f}"
    N[f"trend_dir_mb_{w[:4]}"] = "above" if v > 0 else "below"

# Baseline model (raw CRU climate, governance imputed without the response) and the
# stored-control specification, both fitted with CausalImpact; refit = custom implementation.
bm = pd.read_csv(T / "baseline_model.csv").set_index("check")
for tag, k in (("base", "baseline_causalimpact"), ("stored", "stored_controls_causalimpact"), ("refit", "baseline_refit")):
    x = bm.loc[k]
    N[f"{tag}_obs"], N[f"{tag}_pred"], N[f"{tag}_eff"] = mha(x.observed_mean_ha), mha(x.predicted_mean_ha), mha(x.effect_mean_ha)
    N[f"{tag}_ci"], N[f"{tag}_p"] = ci(x.effect_low_ha, x.effect_high_ha), f"{x.tail_probability:.3f}"
N["refit_gap"] = f"{abs(bm.loc['baseline_refit', 'effect_mean_ha'] - bm.loc['baseline_causalimpact', 'effect_mean_ha']) / 1e6:.2f}"
r = pd.read_csv(T / "bsts_robustness.csv").set_index("check")
for k in r[r.group != "Placebo"].index:
    key = k.split("_")[0]
    N[f"eff_{key}"] = signed(r.loc[k, "effect_mean_ha"])
    N[f"ci_{key}"] = ci(r.loc[k, "effect_low_ha"], r.loc[k, "effect_high_ha"])
    N[f"p_{key}"] = f"{r.loc[k, 'tail_probability']:.3f}"
    N[f"pred_{key}"] = mha(r.loc[k, "predicted_mean_ha"])
pl = r[r.group == "Placebo"]
N["placebo_level_range"] = (f"{pl[pl.trend == 'level'].effect_mean_ha.min() / 1e6:+.2f} to "
                            f"{pl[pl.trend == 'level'].effect_mean_ha.max() / 1e6:+.2f}").replace("+", "+")
N["placebo_level_mean"] = signed(pl[pl.trend == "level"].effect_mean_ha.mean())
N["placebo_llt_mean"] = signed(pl[pl.trend == "local_linear"].effect_mean_ha.mean())
N["n_placebo_excl"] = str(int(pl.interval_excludes_zero.sum()))
N["n_checks"] = str(int((r.group != "Placebo").sum() - 1))
N["n_checks_excl"] = str(int(r[(r.group != "Placebo") & (r.index != "0_baseline")].interval_excludes_zero.sum()))
inc = pd.read_csv(T / "baseline_inclusion_probabilities.csv").set_index("variable")
N["inc_cor_con"] = f"{inc.loc['cor_con', 'inclusion_probability']:.2f}"
N["inc_temp"] = f"{inc.loc['temp', 'inclusion_probability']:.2f}"

# Placebos at every pre-tariff year and post-period split (analysis/10).
pa = pd.read_csv(T / "placebo_all_years.csv")
lv, ll = pa[pa.trend == "level"], pa[pa.trend == "local_linear"]
N["pa_lv_min"], N["pa_lv_max"] = signed(lv.effect_mean_ha.min()), signed(lv.effect_mean_ha.max())
N["pa_lv_npos"] = str(int((lv.effect_mean_ha > 0).sum()))
N["pa_lv_nexcl"] = str(int(lv.interval_excludes_zero.sum()))
N["pa_lv_excl_years"] = "–".join(str(y) for y in (lv[lv.interval_excludes_zero].placebo_year.min(),
                                                   lv[lv.interval_excludes_zero].placebo_year.max()))
N["pa_ll_nexcl"] = str(int(ll.interval_excludes_zero.sum()))
N["pa_ll_min"], N["pa_ll_max"] = signed(ll.effect_mean_ha.min()), signed(ll.effect_mean_ha.max())
sp = pd.read_csv(T / "post_period_split.csv")
for tr, tk in (("level", "lv"), ("local_linear", "ll")):
    for lab, wk in (("2019-2022 (Bolsonaro)", "b"), ("2023-2024 (Lula)", "l")):
        x = sp[(sp.trend == tr) & (sp.check == lab)].iloc[0]
        N[f"split_{tk}_{wk}"] = signed(x.effect_mean_ha)
        N[f"split_{tk}_{wk}_ci"] = ci(x.effect_low_ha, x.effect_high_ha)
    c = pd.read_csv(T / "post_period_contrast.csv").set_index("trend").loc[tr]
    N[f"contrast_{tk}"] = signed(c.difference_mean_ha)
    N[f"contrast_{tk}_ci"] = ci(c.difference_low_ha, c.difference_high_ha)

# State map (analysis/11).
sm = pd.read_csv(T / "state_map_values.csv").set_index("state")
N["mt_net"] = f"{sm.loc['Mato Grosso', 'net_change_mha']:.2f}"
top6 = sm.net_change_mha.nlargest(6)
N["top6_net_pct"] = f"{100 * top6.sum() / sm.net_change_mha.sum():.0f}"
mato = sm.loc[["Maranhao", "Tocantins", "Piaui", "Bahia"]]
N["matopiba_w5"] = f"{100 * mato.all_native_w5_ha.sum() / mato.all_eligible5_ha.sum():.1f}"
N["matopiba_native_share"] = f"{100 * mato.all_native_w5_ha.sum() / sm.all_native_w5_ha.sum():.0f}"
for st, k in (("Piaui", "pi"), ("Maranhao", "ma"), ("Rio Grande Do Sul", "rs"), ("Mato Grosso", "mt"),
              ("Roraima", "rr")):
    N[f"w5_{k}"] = f"{sm.loc[st, 'native_w5_pct']:.1f}"
_sa = pd.read_csv(V2 / "state_annual_areas.csv")
_sa = _sa[_sa.year.between(2019, 2024)].groupby("state")[["all_native_w5_ha", "all_woody_w5_ha", "all_nonwoody_w5_ha"]].sum()
N["rs_nonwoody_pct"] = f"{100 * _sa.loc['Rio Grande Do Sul', 'all_nonwoody_w5_ha'] / _sa.loc['Rio Grande Do Sul', 'all_native_w5_ha']:.0f}"
_m = _sa.loc[["Maranhao", "Tocantins", "Piaui", "Bahia"]].sum()
N["matopiba_woody_pct"] = f"{100 * _m.all_woody_w5_ha / _m.all_native_w5_ha:.0f}"
N["rs_native_share"] = f"{100 * sm.loc['Rio Grande Do Sul', 'all_native_w5_ha'] / sm.all_native_w5_ha.sum():.0f}"

# Land-use link (v2 accounting), 2019-2024.
lu = pd.read_csv(T / "land_use_link_summary.csv").set_index("measure")["value"]
N["entry"] = f"{lu['Gross soybean entry']:.2f}"
N["exit"] = f"{lu['Soybean exit']:.2f}"
N["net"] = f"{lu['Net soybean-area change']:.2f}"
N["reentry_pct"] = f"{lu['Re-entry share of entry']:.1f}"
N["first_pct"] = f"{lu['First observed entry share of entry']:.1f}"
N["managed_pct"] = f"{lu['Managed land immediately before entry']:.1f}"
N["native_now_pct"] = f"{lu['Native cover immediately before entry']:.1f}"
N["w1"] = f"{lu['Native cover within 1 year, all entry']:.1f}"
N["w3"] = f"{lu['Native cover within 3 years, all entry']:.1f}"
N["w5"] = f"{lu['Native cover within 5 years, all entry']:.1f}"
N["w5_first"] = f"{lu['Native cover within 5 years, first observed entry']:.1f}"
N["w5_re"] = f"{lu['Native cover within 5 years, re-entry']:.1f}"
N["w5_mha"] = f"{lu['Entry with native cover within 5 years']:.2f}"
o = pd.read_csv(T / "soybean_entry_origins_by_period.csv")
o = o[o.period == "2019-2024"].set_index("origin")["share_pct"]
N["o_agri"] = f"{o['other_agriculture']:.1f}"
N["o_past"] = f"{o['pasture']:.1f}"
N["o_mosaic"] = f"{o['mosaic']:.1f}"
N["o_woody"] = f"{o['woody']:.1f}"
N["o_nonwoody"] = f"{o['nonwoody']:.1f}"

# Land use by period (p18 = 2018, pp = 2019-2024 model post-period, p7 = 2018-2024).
_lp = pd.read_csv(T / "land_use_by_period.csv").set_index(["period", "population"])
for per, tag in (("2018", "p18"), ("2019-2024", "pp"), ("2018-2024", "p7")):
    for pop, ptag in (("all", ""), ("first", "_first")):
        x = _lp.loc[(per, pop)]
        N[f"{tag}_entry{ptag}"] = f"{x.entry_mha:.2f}"
        N[f"{tag}_managed{ptag}"] = f"{x.prior_managed_pct:.1f}"
        N[f"{tag}_native1{ptag}"] = f"{x.prior_native_pct:.1f}"
        N[f"{tag}_other1{ptag}"] = f"{x.prior_other_pct:.1f}"
        N[f"{tag}_w5{ptag}"] = f"{x.native_w5_pct:.1f}"
        N[f"{tag}_w5woody{ptag}"] = f"{x.native_w5_woody_pct:.1f}"
        N[f"{tag}_w5nonwoody{ptag}"] = f"{x.native_w5_nonwoody_pct:.1f}"
        N[f"{tag}_earlier{ptag}"] = f"{x.native_earlier_only_pct:.1f}"
        N[f"{tag}_earlier_mha{ptag}"] = f"{x.native_earlier_only_mha:.2f}"
        N[f"{tag}_seqmin{ptag}"] = f"{x.native_then_managed_min_pct:.1f}"
        N[f"{tag}_w5_mha{ptag}"] = f"{x.native_w5_mha:.2f}"

# Exposure models (v2).
em = pd.read_csv(V2 / "Table_4_exposure_models.csv").set_index("model")
pt = pd.read_csv(V2 / "Table_5_pretrend_tests.csv")
fmt = lambda v: f"{'−' if v < 0 else ''}{abs(v):.3f}"
for k, key in (("primary_share", "st"), ("all_municipalities_china_share", "mu"),
               ("state_year_shock_absorption", "sy")):
    N[f"{key}_b"] = fmt(em.loc[k, "estimate"])
    N[f"{key}_ci"] = f"{fmt(em.loc[k, 'ci_low'])} to {fmt(em.loc[k, 'ci_high'])}"
N["st_p"] = f"{em.loc['primary_share', 'p_value']:.2f}"


def sci(p):
    m, e = f"{p:.1e}".split("e")
    return f"{m} × 10{{sup}}{int(e)}{{/sup}}".replace("-", "−")


pv = dict(zip(pt["sample"] + "|" + pt.lead_window, pt.p_value))
N["pt_st_recent"] = f"{pv['State / recent|2012-2016']:.2f}"
N["pt_st_long"] = f"{pv['State / long|2004-2016']:.3f}"
N["pt_mu_recent"] = sci(pv["Municipality / recent|2012-2016"])
N["pt_sy_recent"] = sci(pv["Municipality / state-year effects|2012-2016"])

TOKEN = re.compile(r"«([a-z0-9_]+)»")


def fill(text):
    def rep_(m):
        if m.group(1) not in N:
            raise KeyError(f"Unknown number key: {m.group(1)}")
        return N[m.group(1)]
    return TOKEN.sub(rep_, text)


if __name__ == "__main__":
    for k, v in N.items():
        print(f"{k:28s} {v}")
