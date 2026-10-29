# Data

## processed/

| File | Content | Source |
|---|---|---|
| `forest_loss.csv` | National annual series, 2001–2024, used by the original model. Byte-identical to `data/processed/forest_loss.csv` in [tariff_war_forest_loss](https://github.com/MustakAhmad08/tariff_war_forest_loss) (SHA-256 `5b243e97f4f332b4af7ad963f81dce61ed77f9211e76cf773061045c6c526d4f`) | Original repository |
| `forest_loss_original_copy.csv` | Unmodified backup copy of `forest_loss.csv` | Copy |
| `cru_ts409_brazil_annual.csv` | Annual national means of temperature, precipitation, and relative humidity for Brazil, CRU TS 4.09, 1901–2024; the baseline climate controls (`analysis/13_control_provenance.py` downloads it once) | World Bank Climate Change Knowledge Portal API |
| `ibge_states_2024_simplified.gpkg` | 27 state outlines dissolved from IBGE 2024 municipal boundaries, simplified with a 2-km tolerance (`analysis/09_prepare_state_boundaries.py`) | IBGE malhas territoriais 2024 |
| `ibge_soy_planted_area_brazil.csv` | IBGE planted soybean area, Brazil, 2001–2024 (PAM table 1612, variable 109) | IBGE SIDRA API, retrieved 18 Oct 2026 for version 2 |

**The file name is historical.** `forest_loss.csv` is not a forest-loss file for the model response. Its column `FCL_Soybean` is total mapped soybean area (MapBiomas class 39). The version 2 audit established this: summing the state–biome soybean-class table reproduces it in every year, and it correlates at 0.9999975 with the MapBiomas national soybean series.

Columns used:

| Column(s) | Use |
|---|---|
| `FCL_Soybean` | Response: total mapped soybean area (ha) |
| `econ_free`, `cor_con`, `gov_eff`, `pol_stab`, `rule_law`, `reg_qual`, `voice_acc` | Governance controls: Heritage Foundation economic freedom and six Worldwide Governance Indicators, each min–max rescaled across a seven-country panel for 2002–2023 (sheet `panel_data` of the compiled workbook). The model standardizes every control, so this rescaling does not affect estimates. Missing for 2001 and 2024 |
| `hum`, `prec`, `temp` | Climate series labelled CCKP in the compiled workbook. They closely resemble a two-sided smooth of the CRU TS 4.09 annual means (`results/tables/climate_provenance.csv`); the original processing is undocumented. Used only in the stored-control comparison; the baseline uses `cru_ts409_brazil_annual.csv` |
| `Soy_ex_BRA_CHINA (Kg)`, `Tot_Soy_Ex_BRA (Kg)` | Brazilian exports, UN Comtrade HS 1201 net weight. Matches the archived Comtrade extract for 2013–2024 and a Comtrade query for 2001. Descriptive only |
| `Soy_Ex_US_CHINA (Kg)`, `Tot_Soy_Ex_US (Kg)` | US exports, USDA FAS GATS (matches the archived GATS extract). Descriptive only |

**Before publication:** check the Brazilian 2002–2012 trade values against UN Comtrade (only 2001 was checked by query), and record which Worldwide Governance Indicators release was used.

## derived/v2_land_use/

These files are copied unchanged from the version 2 repository (`revised manuscript/tables/` and `data/derived/manuscript/source_data/`). They hold the MapBiomas Collection 10.1 transition accounting and the exposure models. Both rest on Earth Engine exports and enforcement panels that are too large to include here.

| File | Content |
|---|---|
| `Table_2_period_accounting.csv` | Entry, exit, net change by period |
| `Table_3_soybean_entry_origins.csv` | Class in the year before entry, 2018–2024 |
| `Table_6_national_entry_histories.csv` | Re-entry / first observed entry and 1-, 3-, 5-year native histories |
| `annual_soy_gain_origins_national.csv` | Annual national entry by origin |
| `Table_4_exposure_models.csv`, `Table_5_pretrend_tests.csv` | Exposure models and lead tests |
| `state_annual_areas.csv` | State-year soybean area, entry, and native histories (Figure 5) |
| `*_event_study.csv` | Event-study coefficients for Figure 6 |

`analysis/06_land_use_link.py` re-checks their accounting identities before use.
