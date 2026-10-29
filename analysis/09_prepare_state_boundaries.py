"""One-off: dissolve IBGE 2024 municipal boundaries to simplified state outlines for Figure 6.

Usage: python analysis/09_prepare_state_boundaries.py <path to BR_Municipios_2024.zip>
The input archive (287 MB, IBGE malhas territoriais 2024) is not stored in this repository;
the output (data/processed/ibge_states_2024_simplified.gpkg) is.
"""
import sys
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]
src = Path(sys.argv[1])
mun = gpd.read_file(f"zip://{src.as_posix()}!BR_Municipios_2024.shp")
print(mun.columns.tolist(), mun.crs, len(mun))
state = mun.dissolve(by=["CD_UF", "NM_UF", "SIGLA_UF"], as_index=False)[["CD_UF", "NM_UF", "SIGLA_UF", "geometry"]]
# Simplify in an equal-area projection (~2 km tolerance), then store in SIRGAS 2000 (EPSG:4674).
state = state.to_crs("ESRI:102033")
state["geometry"] = state.geometry.simplify(2000, preserve_topology=True)
state = state.to_crs(mun.crs)
assert len(state) == 27, len(state)
out = ROOT / "data" / "processed" / "ibge_states_2024_simplified.gpkg"
state.to_file(out, driver="GPKG")
print(out, len(state))
