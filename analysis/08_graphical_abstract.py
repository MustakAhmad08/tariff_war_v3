"""Graphical abstract (square, 1500 x 1500 px): trade, area versus counterfactual, land origins."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T = ROOT / "results" / "tables"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, BAND = "#0b0b0b", "#52514e", "#8a8984", "#d9d8d3"
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.linewidth": 0.6})

tr = pd.read_csv(T / "trade_restructuring_annual.csv")
rs = pd.read_csv(T / "bsts_robustness_series.csv")

fig = plt.figure(figsize=(5, 5), dpi=300)
fig.text(0.03, 0.965, "United States–China tariff dispute and Brazilian soybean expansion", fontsize=10,
         fontweight="bold", color=INK)

a = fig.add_axes([0.11, 0.56, 0.34, 0.30])
a.plot(tr.year, tr.brazil_to_china_mt, color=BLUE, lw=2)
a.plot(tr.year, tr.us_to_china_mt, color=ORANGE, lw=2)
a.axvline(2018, color=MUTED, lw=0.7, ls=(0, (3, 2)))
a.lines[0].set_label("Brazil → China"); a.lines[1].set_label("United States → China")
a.legend(loc="upper left", fontsize=7.5, frameon=False, handlelength=1.4)
a.set_ylim(0, 105)  # Headroom for the legend.
a.set_ylabel("Exports (million tonnes)", fontsize=8); a.tick_params(labelsize=7)
a.set_title("1  Trade shifted to Brazil", loc="left", fontsize=9, color=INK)

b = fig.add_axes([0.62, 0.56, 0.34, 0.30])
for k, col, ls, lab in [("0_baseline", INK2, (0, (4, 2)), "Baseline model"),
                        ("2a_local_linear_trend", AQUA, (0, (1, 1.2)), "With trend")]:
    d = rs[rs.check == k]
    b.plot(d.year, d.predicted_ha / 1e6, color=col, lw=1.4, ls=ls)
d = rs[rs.check == "0_baseline"]
b.plot(d.year, d.observed_ha / 1e6, color=BLUE, lw=2)
b.axvline(2018.5, color=MUTED, lw=0.7, ls=(0, (3, 2)))
b.lines[0].set_label("Counterfactual, baseline"); b.lines[1].set_label("Counterfactual, with trend")
b.lines[2].set_label("Observed")
h, l = b.get_legend_handles_labels()
b.legend([h[2], h[0], h[1]], [l[2], l[0], l[1]], loc="lower right", fontsize=7, frameon=False, handlelength=1.6)
b.set_ylim(2, 43)  # Room below the series for the legend.
b.set_ylabel("Soybean area (million hectares)", fontsize=8); b.tick_params(labelsize=7)
b.set_title("2  Area kept growing; no robust\n    excess over pre-2018 path", loc="left", fontsize=9, color=INK)

c = fig.add_axes([0.11, 0.33, 0.85, 0.09])
# Same period as the model's post-period (2019-2024), as in the Summary.
lp = pd.read_csv(ROOT / "results" / "tables" / "land_use_by_period.csv").set_index(["period", "population"])
pp = lp.loc[("2019-2024", "all")]
managed, native, other = pp.prior_managed_pct, pp.prior_native_pct, pp.prior_other_pct
left = 0
for v, col, lab in [(managed, INK2, f"Managed land {managed:.1f}%"), (native, AQUA, ""), (other, MUTED, "")]:
    c.barh(0, v, left=left, color=col, height=0.6, edgecolor="white", linewidth=1)
    left += v
c.text(managed / 2, 0, f"Managed land before entry: {managed:.1f}%", color="white", ha="center", va="center", fontsize=8.5)
c.set_xlim(0, 100); c.set_yticks([]); c.spines["left"].set_visible(False)
c.set_xlabel("Share of 2019–2024 soybean entry, class in the year before entry (%)", fontsize=8)
c.tick_params(labelsize=7)
c.set_title("3  Land before soybean", loc="left", fontsize=9, color=INK)

fig.text(0.11, 0.15,
         f"• {pp.native_w5_pct:.1f}% had native vegetation within 5 years ({pp.native_w5_mha:.2f} million hectares),\n"
         f"   including at least {pp.native_then_managed_min_pct:.1f}% that went native → managed → soybean\n"
         "• Native vegetation includes savanna and grassland, not only forest\n"
         "• Shifts in location and pasture displacement are not measured\n"
         "• Forest loss is neither attributed to the tariff nor ruled out", fontsize=8.5, color=INK, va="center",
         linespacing=1.5)
out = ROOT / "results" / "figures" / "Graphical_abstract.png"
fig.savefig(out, dpi=300)
fig.savefig(out.with_suffix(".pdf"))
print(out)
