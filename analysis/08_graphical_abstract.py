"""Square graphical abstract; all quantitative labels read from analysis tables."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
parser.add_argument("--output-dir", type=Path)
args = parser.parse_args()
T = args.root / "results" / "tables"
OUT = args.output_dir or args.root / "results" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

BLUE, ORANGE, GREEN = "#2a78d6", "#d86432", "#168765"
INK, GRAY, LIGHT = "#182b37", "#53616a", "#e8edef"
plt.rcParams.update({"font.family": "Arial", "font.size": 9,
                     "text.color": INK, "axes.labelcolor": GRAY,
                     "xtick.color": GRAY, "pdf.fonttype": 42,
                     "ps.fonttype": 42})
trade = pd.read_csv(T / "trade_restructuring_annual.csv").set_index("year")
baseline = pd.read_csv(T / "baseline_model.csv").set_index("check").loc["baseline_causalimpact"]
trend = pd.read_csv(T / "bsts_robustness.csv").set_index("check").loc["2a_local_linear_trend"]
land = pd.read_csv(T / "land_use_by_period.csv").set_index(["period", "population"]).loc[("2019-2024", "all")]

fig = plt.figure(figsize=(6, 6), dpi=300, facecolor="white")
def txt(x, y, s, size=9, color=INK, weight="normal", **kwargs):
    return fig.text(x, y, s, fontsize=size, color=color, weight=weight, **kwargs)

def heading(n, y, title):
    txt(.06, y, f"{n:02d}", 10, BLUE, "bold")
    txt(.115, y, title, 11.5, INK, "bold")

txt(.06, .953, "US–China tariffs and", 17, weight="bold")
txt(.06, .911, "Brazilian soybean expansion", 17, weight="bold")

heading(1, .849, "Soybean trade shifted toward Brazil")
txt(.115, .817, "Exports to China · 2017 → 2018 · million tonnes", 9, GRAY)

# Two direct comparisons; the arrows indicate time, not a causal pathway.
for x, name, column, color in [(.115, "United States", "us_to_china_mt", ORANGE),
                               (.575, "Brazil", "brazil_to_china_mt", BLUE)]:
    v0, v1 = trade.loc[2017, column], trade.loc[2018, column]
    change = 100 * (v1 / v0 - 1)
    txt(x, .776, name, 10, color, "bold")
    txt(x, .731, f"{v0:.1f} → {v1:.1f}", 19, color, "bold")
    txt(x, .700, f"{change:+.0f}%".replace("-", "−"), 10, color, "bold")

heading(2, .638, "Soybean-area estimates depend on the model")
txt(.115, .606, "Mean observed − counterfactual area · 2019–2024", 9, GRAY)

ax = fig.add_axes([.335, .463, .51, .116])
ax.set_xlim(-10, 10)
ax.set_ylim(-.55, 1.55)
ax.axvline(0, color="#9ba7ae", lw=.8, ls=(0, (3, 3)))
for y, row, color, name in [(1, baseline, BLUE, "Baseline"), (0, trend, GREEN, "Local linear trend")]:
    mean, low, high = [row[c] / 1e6 for c in ("effect_mean_ha", "effect_low_ha", "effect_high_ha")]
    ax.plot([low, high], [y, y], color=color, lw=2.2, solid_capstyle="round")
    ax.scatter([mean], [y], s=38, color=color, zorder=3)
    ax.text(-.045, y, name, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=9)
    ax.text(1.05, y, f"{mean:+.2f}".replace("-", "−"), transform=ax.get_yaxis_transform(),
            va="center", fontsize=10, color=color, weight="bold")
ax.set_yticks([])
ax.set_xticks([-10, -5, 0, 5, 10])
ax.tick_params(axis="x", labelsize=8, length=2, pad=3)
for spine in ax.spines.values():
    spine.set_visible(False)
txt(.59, .412, "Million hectares · points: means; lines: 95% posterior intervals", 8,
    GRAY, ha="center")

heading(3, .355, "Most soybean entry followed managed land")
txt(.115, .323, "2019–2024 gross entry · two overlapping history measures", 8.6, GRAY)

for x, value, color, label in [
    (.115, land.prior_managed_pct, INK, "Managed land\nin the previous year"),
    (.575, land.native_w5_pct, GREEN, "Native cover in any of\nthe preceding five years")
]:
    txt(x, .258, f"{value:.1f}%", 27, color, "bold")
    txt(x, .207, label, 9, GRAY, linespacing=1.4)
    bar = fig.add_axes([x, .171, .35, .012])
    bar.barh(0, 100, height=1, color=LIGHT)
    bar.barh(0, value, height=1, color=color)
    bar.set_xlim(0, 100)
    bar.set_ylim(-.5, .5)
    bar.axis("off")

txt(.115, .139, "Native cover includes forest, savanna, and grassland.", 8, GRAY)
txt(.06, .073, "Tariff-driven expansion is not established.", 10.2, weight="bold")
txt(.06, .044, "Indirect forest loss is not ruled out.", 10.2, weight="bold")

for suffix in ("png", "pdf"):
    fig.savefig(OUT / f"Graphical_abstract.{suffix}", dpi=300, facecolor="white")
plt.close(fig)
print(OUT / "Graphical_abstract.png")
