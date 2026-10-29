"""Figure 5: state maps of net soybean-area change and recent native-cover history, 2019-2024
(the post-period of the BSTS model).

Reviewer 1, comment 4: each panel has its own legend, a scale bar, and a north arrow.
Data: version 2 state accounting (MapBiomas Collection 10.1); IBGE 2024 state outlines.
"""
import unicodedata
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap, ListedColormap
from matplotlib.patches import FancyArrow, Patch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "results" / "figures"
T = ROOT / "results" / "tables"
INK, INK2, NODATA, EDGE = "#0b0b0b", "#52514e", "#ecebe7", "#ffffff"
BLUES = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # sequential blue steps 100-700
ORANGES = [LinearSegmentedColormap.from_list("o", ["#fde3d6", "#eb6834", "#7a2a0b"])(v)
           for v in np.linspace(0.0, 1.0, 5)]  # single-hue ramp through categorical orange
MIN_ENTRY_HA = 10_000  # below this, a share is not mapped
MM = 1 / 25.4
plt.rcParams.update({"font.family": "Arial", "font.size": 7, "pdf.fonttype": 42})


def key(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return s.replace(" ", "")


s = pd.read_csv(ROOT / "data" / "derived" / "v2_land_use" / "state_annual_areas.csv")
area = s.pivot(index="state", columns="year", values="current_soy_ha")
p = s[s.year.between(2019, 2024)].groupby("state")[["all_entry_ha", "all_eligible5_ha", "all_native_w5_ha"]].sum()
p["net_change_mha"] = (area[2024] - area[2018]) / 1e6
p["native_w5_pct"] = np.where(p.all_eligible5_ha >= MIN_ENTRY_HA, 100 * p.all_native_w5_ha / p.all_eligible5_ha, np.nan)
nat = pd.read_csv(T / "land_use_by_period.csv").set_index(["period", "population"]).loc[("2019-2024", "all")]
assert abs(p.all_native_w5_ha.sum() / p.all_eligible5_ha.sum() * 100 - nat.native_w5_pct) < 0.01
p.reset_index().round(4).to_csv(T / "state_map_values.csv", index=False)

geo = gpd.read_file(ROOT / "data" / "processed" / "ibge_states_2024_simplified.gpkg")
geo["k"] = geo.NM_UF.map(key)
p["k"] = [key(n) for n in p.index]
g = geo.merge(p, on="k", how="left").to_crs("ESRI:102033")  # South America Albers equal area (m)
assert g.all_entry_ha.notna().all(), g[g.all_entry_ha.isna()].NM_UF.tolist()


def scale_bar(ax, km=1000):
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    x, y, h = x0 + 0.66 * (x1 - x0), y0 + 0.05 * (y1 - y0), 0.012 * (y1 - y0)
    for i in range(2):
        ax.add_patch(Rectangle((x + i * km * 500, y), km * 500, h, facecolor=INK if i == 0 else "white",
                               edgecolor=INK, linewidth=0.5))
    for v in (0, km // 2, km):
        ax.text(x + v * 1000, y + 2.2 * h, f"{v}", ha="center", va="bottom", fontsize=6, color=INK2)
    ax.text(x + km * 1000 + 0.02 * (x1 - x0), y + h / 2, "km", va="center", fontsize=6, color=INK2)


def north_arrow(ax):
    ax.add_patch(FancyArrow(0.93, 0.83, 0, 0.06, width=0.005, head_width=0.03, head_length=0.03,
                            transform=ax.transAxes, color=INK))
    ax.text(0.93, 0.925, "N", transform=ax.transAxes, ha="center", va="bottom", fontsize=8, fontweight="bold")


fig, axs = plt.subplots(1, 2, figsize=(174 * MM, 92 * MM))
panels = [
    ("net_change_mha", [0, 0.05, 0.2, 0.4, 0.8, 1.4], BLUES, "Net change, 2018–2024\n(million ha)",
     ["< 0.05", "0.05–0.2", "0.2–0.4", "0.4–0.8", "≥ 0.8"], "A", "Net change in mapped soybean area"),
    ("native_w5_pct", [0, 2, 5, 10, 25, 60], ORANGES, "2019–2024 entry with native\nvegetation in the previous\n5 years (%)",
     ["< 2", "2–5", "5–10", "10–25", "≥ 25"], "B", "Recent native-vegetation history of entry"),
]
for ax, (col, bins, colors, legend_title, labels, letter, title) in zip(axs, panels):
    cmap, norm = ListedColormap(colors), BoundaryNorm(bins, len(colors))
    has = g[g[col].notna()]
    has.plot(ax=ax, color=[cmap(norm(min(v, bins[-1] - 1e-9))) for v in has[col]], edgecolor=EDGE, linewidth=0.5)
    g[g[col].isna()].plot(ax=ax, color=NODATA, edgecolor=EDGE, linewidth=0.5, hatch="////")
    ax.set_axis_off(); ax.set_aspect("equal")
    handles = [Patch(facecolor=c, edgecolor="none", label=l) for c, l in zip(colors, labels)]
    if g[col].isna().any():
        handles.append(Patch(facecolor=NODATA, edgecolor=INK2, hatch="////", linewidth=0.3,
                             label=f"Entry < {MIN_ENTRY_HA // 1000:,} thousand ha"))
    ax.legend(handles=handles, title=legend_title, loc="lower left", bbox_to_anchor=(-0.01, 0.0), fontsize=6, title_fontsize=6.3,
              frameon=False, alignment="left")
    scale_bar(ax); north_arrow(ax)
    ax.text(0.0, 1.02, letter, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom")
    ax.text(0.07, 1.02, title, transform=ax.transAxes, fontsize=7.5, va="bottom", color=INK)
fig.text(0.5, 0.01, "Projection: South America Albers equal-area conic. State boundaries: IBGE 2024. "
         "Soybean data: MapBiomas Collection 10.1.", ha="center", fontsize=5.8, color=INK2)
fig.subplots_adjust(wspace=0.02, left=0.01, right=0.99, top=0.93, bottom=0.05)
for ext in ("pdf", "png", "tiff"):
    kw = {"pil_kwargs": {"compression": "tiff_lzw"}} if ext == "tiff" else {}
    fig.savefig(FIG / f"Figure_5_state_maps.{ext}", dpi=600, **kw)
print("Figure 5 written")
