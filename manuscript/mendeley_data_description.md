# Mendeley Data deposit (draft)

**Title:** Data and code for: Brazilian soybean expansion and land-use histories during the US–China tariff dispute

**Description:**
National annual series (2001–2024) of mapped soybean area in Brazil (MapBiomas Collection 10.1, class 39), the governance and climate controls of the Bayesian structural time-series model (including annual CRU TS 4.09 climate means), and soybean trade volumes (UN Comtrade, USDA FAS GATS). The deposit also includes:

- IBGE planted soybean area;
- simplified IBGE 2024 state outlines;
- state and national land-use accounting of soybean entry (version 2 outputs);
- every derived table reported in the article.

The analysis code (R and Python) reproduces all results, figures, and tables.

The file `forest_loss.csv` keeps its original name for reproducibility. Its column `FCL_Soybean` is total soybean area, not forest loss.

**Files to upload:**

- `data/processed/`: `forest_loss.csv`, `cru_ts409_brazil_annual.csv`, `ibge_soy_planted_area_brazil.csv`, `ibge_states_2024_simplified.gpkg`
- `data/derived/v2_land_use/`: all files
- `results/tables/`: all CSV files
- the repository archive: code, `README.md`, `LICENSE`

**Keywords:** soybean; Brazil; tariff dispute; land-use change; Bayesian structural time series; MapBiomas

**License:** CC BY 4.0 for data; MIT for code (as in `LICENSE`).

After the deposit is published, add its DOI to the key resources table and to Data and code availability in `manuscript/iScience_manuscript_v3_R1.docx`.
