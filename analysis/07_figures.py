"""Build main and supplemental figures (Cell Press widths: 85, 114, 174 mm).

Palette: first three slots of the validated categorical palette (blue, orange, aqua),
plus neutral grays for counterfactuals and reference lines. Text stays in ink colors.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
V2 = ROOT / "data" / "derived" / "v2_land_use"
FIG = ROOT / "results" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#d9d8d3"
MM = 1 / 25.4
plt.rcParams.update({
    "font.family": "Arial", "font.size": 7, "axes.titlesize": 7.5, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 600,
})


def panel(ax, letter):
    ax.text(-0.14, 1.06, letter, transform=ax.transAxes, fontsize=9, fontweight="bold",
            color=INK, va="bottom")


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def tariff_line(ax, x=2018):
    ax.axvline(x, color=MUTED, linewidth=0.7, linestyle=(0, (3, 2)))


def save(fig, name):
    for ext in ("pdf", "png", "tiff"):
        kw = {"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tiff" else {}
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig)


# Figure 1. Trade restructuring.
tr = pd.read_csv(T / "trade_restructuring_annual.csv")
fig, (a, b) = plt.subplots(1, 2, figsize=(174 * MM, 62 * MM))
a.plot(tr.year, tr.brazil_to_china_mt, color=BLUE, lw=2, marker="o", ms=3)
a.plot(tr.year, tr.us_to_china_mt, color=ORANGE, lw=2, marker="o", ms=3)
a.text(2024.3, tr.brazil_to_china_mt.iloc[-1], "Brazil → China", color=INK, va="center")
a.text(2024.3, tr.us_to_china_mt.iloc[-1], "U.S. → China", color=INK, va="center")
a.annotate("2018: −74%", (2018, tr.set_index("year").us_to_china_mt[2018]), xytext=(2009.5, 4),
           color=INK2, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
tariff_line(a); grid(a)
a.set(xlabel="Year", ylabel="Soybean exports to China (Mt)", xlim=(2000.5, 2024.5), ylim=(0, None))
a.set_title("Exports to China by supplier", loc="left", color=INK)
panel(a, "A")
b.plot(tr.year, tr.brazil_share_of_us_brazil_supply_to_china_pct, color=BLUE, lw=2, marker="o", ms=3,
       label="Brazil's share of U.S. + Brazil supply to China")
b.plot(tr.year, tr.china_share_of_brazil_exports_pct, color=AQUA, lw=2, marker="o", ms=3,
       label="China's share of Brazil's exports")
b.legend(loc="lower right")
tariff_line(b); grid(b)
b.set(xlabel="Year", ylabel="Share (%)", xlim=(2000.5, 2024.5), ylim=(0, 100))
b.set_title("Market shares", loc="left", color=INK)
panel(b, "B")
fig.subplots_adjust(wspace=0.45)
save(fig, "Figure_1_trade_restructuring")

# Figure 2. Baseline BSTS model: observed versus counterfactual soybean area.
s = pd.read_csv(T / "baseline_model_series.csv")
fig, (a, b) = plt.subplots(1, 2, figsize=(174 * MM, 64 * MM))
a.fill_between(s.year, s.predicted_low_ha / 1e6, s.predicted_high_ha / 1e6, color=BAND, lw=0)
a.plot(s.year, s.predicted_ha / 1e6, color=INK2, lw=1.5, linestyle=(0, (4, 2)))
a.plot(s.year, s.observed_ha / 1e6, color=BLUE, lw=2)
a.text(2024.3, s.observed_ha.iloc[-1] / 1e6, "Observed", color=INK, va="center")
a.text(2024.3, s.predicted_ha.iloc[-1] / 1e6, "Counterfactual\n(95% interval)", color=INK2, va="center")
tariff_line(a, 2018.5); grid(a)
a.set(xlabel="Year", ylabel="Mapped soybean area (Mha)", xlim=(2001.5, 2024.5))
a.set_title("Baseline model, total soybean area", loc="left", color=INK)
panel(a, "A")
post = s[s.period == "post"]
diff = (post.observed_ha - post.predicted_ha) / 1e6
lo = (post.observed_ha - post.predicted_high_ha) / 1e6
hi = (post.observed_ha - post.predicted_low_ha) / 1e6
b.axhline(0, color=INK2, lw=0.7)
b.vlines(post.year, lo, hi, color=BLUE, lw=2)
b.plot(post.year, diff, "o", color=BLUE, ms=5, mec="white", mew=1)
grid(b)
b.set(xlabel="Year", ylabel="Observed − counterfactual (Mha)", xticks=post.year)
b.set_title("Annual deviation (95% interval)", loc="left", color=INK)
panel(b, "B")
fig.subplots_adjust(wspace=0.55)
save(fig, "Figure_2_baseline_bsts")

# Figure 3. Robustness of the average 2019-2024 deviation.
r = pd.read_csv(T / "bsts_robustness.csv")
labels = {
    "0_baseline": "Baseline specification",
    "9_niter_10000": "10,000 MCMC iterations",
    "5_impute_with_response": "Imputation with response",
    "11a_stored_controls": "Stored climate and imputation",
    "11b_stored_controls_local_linear": "Stored controls, local linear trend",
    "3c_governance_only_local_linear": "Local linear trend, governance only",
    "10_post_from_2018": "Post-period from 2018",
    "6a_start_2001": "Training from 2001", "6b_start_2005": "Training from 2005",
    "6c_start_2008": "Training from 2008",
    "3_climate_controls_only": "Climate controls only", "3b_governance_only": "Governance controls only",
    "4a_no_controls": "No controls",
    "2a_local_linear_trend": "Local linear trend", "2b_semilocal_trend": "Semilocal linear trend",
    "4b_no_controls_local_linear": "Local linear trend, no controls",
    "8a_ibge_planted_area": "IBGE planted area", "8b_ibge_local_linear": "IBGE, local linear trend",
}
order = ["0_baseline", "9_niter_10000", "5_impute_with_response", "10_post_from_2018",
         "6a_start_2001", "6b_start_2005", "6c_start_2008", "3_climate_controls_only",
         "3b_governance_only", "4a_no_controls", "8a_ibge_planted_area", "11a_stored_controls",
         "2a_local_linear_trend", "2b_semilocal_trend", "3c_governance_only_local_linear",
         "4b_no_controls_local_linear", "8b_ibge_local_linear", "11b_stored_controls_local_linear"]
plac = r[r.group == "Placebo"].copy()
plac["label"] = plac.apply(lambda x: f"Placebo {x.post_start}–{x.post_end}, "
                           + ("local level" if x.trend == "level" else "local linear"), axis=1)
main = r.set_index("check").loc[order].reset_index()
main["label"] = main.check.map(labels)
rows = pd.concat([main, plac], ignore_index=True)
fig, ax = plt.subplots(figsize=(114 * MM, 130 * MM))
# One empty row separates the placebo block, and carries its heading.
gap = len(plac)
ypos = [y + (1 if y >= gap else 0) for y in range(len(rows))][::-1]
for y, (_, x) in zip(ypos, rows.iterrows()):
    col = MUTED if x.group == "Placebo" else (BLUE if x.check == "0_baseline" else INK2)
    trend = x.trend != "level"
    ax.hlines(y, x.effect_low_ha / 1e6, x.effect_high_ha / 1e6, color=col, lw=2)
    ax.plot(x.effect_mean_ha / 1e6, y, "o" if not trend else "D", ms=5 if not trend else 4.5,
            color=col if not trend else "white", mec=col, mew=1.2)
ax.axvline(0, color=INK2, lw=0.7)
ax.axhline(gap + 0.5, color=GRID, lw=0.8)
ax.set_yticks(ypos, rows.label)
ax.set_xlabel("Average deviation, observed − counterfactual (Mha)")
ax.text(-0.02, gap, "Placebo dates before 2018 (expected ≈ 0)", color=INK, fontweight="bold",
        transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.5)
ax.plot([], [], "o", color=INK2, ms=5, label="Local-level model")
ax.plot([], [], "D", color="white", mec=INK2, mew=1.2, ms=4.5, label="Model with trend term")
ax.legend(loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2)
grid(ax, "x")
save(fig, "Figure_3_bsts_robustness")

# Figure 4. Land-use origins and histories of soybean entry, 2019-2024 (v2 accounting).
h = pd.read_csv(T / "native_history_by_entry_group.csv").set_index("population")
o = pd.read_csv(T / "soybean_entry_origins_by_period.csv")
o = o[o.period == "2019-2024"].set_index("origin")
fig = plt.figure(figsize=(174 * MM, 62 * MM))
gs = fig.add_gridspec(1, 3, width_ratios=[0.9, 1.5, 1.4], wspace=1.05)
a = fig.add_subplot(gs[0])
re_, fi = h.loc["reentry", "entry_mha"], h.loc["first", "entry_mha"]
a.bar(0, re_, color=BLUE, width=0.6)
a.bar(0, fi, bottom=re_ + 0.05, color=ORANGE, width=0.6)
a.text(0.38, re_ / 2, f"Re-entry\n{re_:.2f} Mha\n({h.loc['reentry', 'entry_share_pct']:.1f}%)", va="center", color=INK)
a.text(0.38, re_ + fi / 2, f"First observed\n{fi:.2f} Mha\n({h.loc['first', 'entry_share_pct']:.1f}%)", va="center", color=INK)
a.set(xlim=(-0.5, 1.6), xticks=[], ylabel="Gross soybean entry, 2019–2024 (Mha)")
a.spines["bottom"].set_visible(False); grid(a)
a.set_title("Entry by history", loc="left", color=INK); panel(a, "A")
b = fig.add_subplot(gs[1])
names = {"other_agriculture": "Other agriculture", "pasture": "Pasture", "mosaic": "Agricultural mosaic",
         "woody": "Native woody", "nonwoody": "Native nonwoody", "nonvegetated": "Nonvegetated",
         "plantation": "Forest plantation"}
oo = o.loc[list(names)]
# Managed and native classes are a different grouping from panels A and C, so they use
# neutral ink and aqua rather than the entry-group hues.
cols = [INK2] * 3 + [AQUA] * 2 + [MUTED] * 2
yy = range(len(oo))[::-1]
b.barh(list(yy), oo.share_pct, color=cols, height=0.65)
for y, v in zip(yy, oo.share_pct):
    b.text(v + 1.5, y, f"{v:.1f}%", va="center", color=INK)
b.set_yticks(list(yy), [names[k] for k in oo.index])
b.set(xlim=(0, 95), xlabel="Share of entry (%)")
grid(b, "x"); b.set_title("Class in the year before entry", loc="left", color=INK); panel(b, "B")
c = fig.add_subplot(gs[2])
groups = [("all", "All entry", INK2), ("first", "First observed", ORANGE), ("reentry", "Re-entry", BLUE)]
w = 0.26
for i, (k, lab, col) in enumerate(groups):
    vals = h.loc[k, ["native_w1_pct", "native_w3_pct", "native_w5_pct"]].to_numpy()
    xs = [j + (i - 1) * (w + 0.03) for j in range(3)]
    c.bar(xs, vals, width=w, color=col, label=lab)
c.set_xticks(range(3), ["1 year", "3 years", "5 years"])
c.set(ylabel="Entry with earlier native vegetation (%)", xlabel="History window")
c.legend(loc="upper left"); grid(c)
c.set_title("Earlier native vegetation", loc="left", color=INK); panel(c, "C")
save(fig, "Figure_4_land_use_link")

# Figure 6. Exposure event studies (v2 models, reported for attribution limits).
st = pd.read_csv(V2 / "actual_forest_loss_exposure_event_study.csv")
mu = pd.read_csv(V2 / "municipality_forest_loss_event_study.csv")
sy = pd.read_csv(V2 / "state_year_event_study.csv")
sy = sy[(sy.specification == "state_year_shock_absorption") & (sy.sample_start == 2012)]
fig, (a, b) = plt.subplots(1, 2, figsize=(174 * MM, 60 * MM))
for ax, frames, title, letter in [
    (a, [(st, BLUE, "State primary-forest loss")], "State primary-forest loss (26 states)", "A"),
    (b, [(mu, BLUE, "Year effects"), (sy, ORANGE, "State-by-year effects")],
     "Municipality woody-class exit (5,503–5,506)", "B")]:
    for k, (df, col, lab) in enumerate(frames):
        dx = (k - (len(frames) - 1) / 2) * 0.22
        ax.vlines(df.year + dx, df.conf_low_95, df.conf_high_95, color=col, lw=1.5)
        ax.plot(df.year + dx, df.estimate, "o", color=col, ms=4, mec="white", mew=0.8, label=lab)
        ax.plot(2017 + dx, 0, "o", color="white", mec=col, ms=4, mew=1)
    ax.axhline(0, color=INK2, lw=0.7); ax.axvline(2017.5, color=MUTED, lw=0.7, ls=(0, (3, 2)))
    ax.set(xlabel="Year (2017 = reference)", ylabel="Coefficient, log(1 + ha) per SD exposure")
    ax.set_xticks(range(2012, 2025, 2)); grid(ax)
    ax.set_title(title, loc="left", color=INK); panel(ax, letter)
b.legend(loc="lower left")
fig.subplots_adjust(wspace=0.4)
save(fig, "Figure_6_exposure_event_studies")

# Figure S1. MapBiomas versus IBGE soybean area, with pre-2018 linear trends.
fl = pd.read_csv(ROOT / "data" / "processed" / "forest_loss.csv").set_index("year")["FCL_Soybean"]
ib = pd.read_csv(ROOT / "data" / "processed" / "ibge_soy_planted_area_brazil.csv").set_index("year")["ibge_planted_soy_ha"]
import numpy as np
fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 62 * MM), sharey=True)
for ax, ser, col, name, letter in [(axs[0], fl, BLUE, "MapBiomas mapped soybean area", "A"),
                                   (axs[1], ib, AQUA, "IBGE planted soybean area", "B")]:
    ax.plot(ser.index, ser / 1e6, color=col, lw=2, marker="o", ms=2.5)
    for (a0, b0), ls in [((2002, 2018), (0, (4, 2))), ((2012, 2018), (0, (1, 1.5)))]:
        x = np.arange(a0, b0 + 1); m, c0 = np.polyfit(x, ser.loc[a0:b0], 1)
        xx = np.arange(a0, 2025)
        ax.plot(xx, (m * xx + c0) / 1e6, color=INK2, lw=1, linestyle=ls)
        ax.text(2024.4, (m * 2024 + c0) / 1e6, f"{a0}–{b0} trend", color=INK2, va="center", fontsize=6)
    tariff_line(ax, 2018.5); grid(ax)
    ax.set(xlabel="Year", xlim=(2001, 2024.5)); ax.set_title(name, loc="left", color=INK); panel(ax, letter)
axs[0].set_ylabel("Soybean area (Mha)")
fig.subplots_adjust(wspace=0.45)
save(fig, "Figure_S1_area_sources_trends")

# Figure S2. Counterfactual paths under alternative specifications.
rs = pd.read_csv(T / "bsts_robustness_series.csv")
pick = [("0_baseline", "Baseline (local level, 10 controls)"), ("2a_local_linear_trend", "Local linear trend"),
        ("3_climate_controls_only", "Climate controls only"), ("3b_governance_only", "Governance controls only"),
        ("4a_no_controls", "No controls"), ("8a_ibge_planted_area", "IBGE planted area")]
fig, axs = plt.subplots(2, 3, figsize=(174 * MM, 100 * MM), sharex=True)
for ax, (k, lab), letter in zip(axs.flat, pick, "ABCDEF"):
    d = rs[rs.check == k]
    ax.fill_between(d.year, d.predicted_low_ha / 1e6, d.predicted_high_ha / 1e6, color=BAND, lw=0)
    ax.plot(d.year, d.predicted_ha / 1e6, color=INK2, lw=1.2, ls=(0, (4, 2)))
    ax.plot(d.year, d.observed_ha / 1e6, color=BLUE, lw=1.6)
    tariff_line(ax, 2018.5); grid(ax)
    ax.set_title(lab, loc="left", color=INK, fontsize=7); panel(ax, letter)
for ax in axs[1]: ax.set_xlabel("Year")
for ax in axs[:, 0]: ax.set_ylabel("Soybean area (Mha)")
fig.subplots_adjust(hspace=0.45, wspace=0.35)
save(fig, "Figure_S2_counterfactual_paths")

# Figure S3. Inclusion probabilities of the baseline controls.
inc = pd.read_csv(T / "baseline_inclusion_probabilities.csv").sort_values("inclusion_probability")
nice = {"econ_free": "Economic freedom", "cor_con": "Control of corruption", "gov_eff": "Government effectiveness",
        "pol_stab": "Political stability", "rule_law": "Rule of law", "reg_qual": "Regulatory quality",
        "voice_acc": "Voice and accountability", "hum": "Humidity", "prec": "Precipitation", "temp": "Temperature"}
fig, ax = plt.subplots(figsize=(85 * MM, 62 * MM))
cols = [AQUA if v in ("hum", "prec", "temp") else BLUE for v in inc.variable]
ax.barh(range(len(inc)), inc.inclusion_probability, color=cols, height=0.65)
for i, v in enumerate(inc.inclusion_probability):
    ax.text(v + 0.02, i, f"{v:.2f}", va="center", color=INK)
ax.set_yticks(range(len(inc)), [nice.get(v, v) for v in inc.variable])
ax.set(xlim=(0, 1.1), xlabel="Posterior inclusion probability")
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=BLUE, label="Governance"), Patch(color=AQUA, label="Climate")],
          loc="lower right"); grid(ax, "x")
save(fig, "Figure_S3_inclusion_probabilities")
# Figure S4. Placebo deviation at every pre-tariff year, with the 2019-2024 estimate.
pa = pd.read_csv(T / "placebo_all_years.csv")
rb = pd.read_csv(T / "bsts_robustness.csv").set_index("check")
fig, ax = plt.subplots(figsize=(114 * MM, 64 * MM))
for tr, col, mk, dx, lab in [("level", INK2, "o", -0.15, "Baseline (local level)"),
                             ("local_linear", AQUA, "D", 0.15, "With local linear trend")]:
    d = pa[pa.trend == tr]
    ax.vlines(d.placebo_year + dx, d.effect_low_ha / 1e6, d.effect_high_ha / 1e6, color=col, lw=1.6)
    ax.plot(d.placebo_year + dx, d.effect_mean_ha / 1e6, mk, color=col, ms=4.5, mec="white", mew=0.8, label=lab)
    k = "0_baseline" if tr == "level" else "2a_local_linear_trend"
    x = rb.loc[k]
    ax.vlines(2019 + dx, x.effect_low_ha / 1e6, x.effect_high_ha / 1e6, color=BLUE if tr == "level" else col, lw=2)
    ax.plot(2019 + dx, x.effect_mean_ha / 1e6, mk, color=BLUE if tr == "level" else col, ms=5.5, mec="white", mew=0.8)
ax.axhline(0, color=INK2, lw=0.7); ax.axvline(2018, color=MUTED, lw=0.7, ls=(0, (3, 2)))
ax.set_xticks(list(range(2008, 2018)) + [2019], [str(y) for y in range(2008, 2018)] + ["Tariff\n2019–24"])
ax.set(xlabel="Pseudo-intervention year (evaluated up to four years, ending by 2017)",
       ylabel="Average deviation (Mha)")
ax.legend(loc="upper right"); grid(ax)
save(fig, "Figure_S4_placebo_by_year")

print("Figures written to", FIG)
