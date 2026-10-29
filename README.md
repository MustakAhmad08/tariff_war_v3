# Brazilian soybean expansion and land-use histories during the US–China tariff dispute (version 3)

Code, data, and manuscript for version 3 of the study. It follows the structure of the original repository, [tariff_war_forest_loss](https://github.com/MustakAhmad08/tariff_war_forest_loss). The core model is a Bayesian structural time-series (CausalImpact) model, with a corrected interpretation and corrected controls:

- **What the model estimates:** the 2019–2024 deviation of Brazil's **total mapped soybean area** from a counterfactual built on 2002–2018 data. It does not estimate forest loss. The earlier claims of 4.5 Mha/yr of additional forest loss and 27.2 Mha of cumulative clearing are withdrawn.
- **Baseline specification:** the original model structure, with raw annual CRU TS 4.09 climate means in place of the compiled file's climate series (which closely resemble a two-sided smooth), and governance values for 2001 and 2024 imputed without the response. The original specification is reproduced exactly as the "stored-control" comparison.
- **Main findings:**
  - Soybean trade shifted from the US to Brazil after 2018, and Brazilian soybean area kept growing.
  - The baseline places mean 2019–2024 area 5.13 Mha above the counterfactual (95% interval 0.48 to 9.57). The deviation moves close to zero when the counterfactual includes a trend, and deviations of similar size appear at every placebo date from 2008 to 2017. It is not a robust basis for tariff attribution; it does not show the effect is zero.
  - In 2019–2024, 97.2% of soybean entry followed managed land in the year before entry. Native vegetation was mapped within five years for 6.1% of all entry and 17.4% of first observed entry; at least 3.4% of all entry went from native vegetation through managed land to soybean (`results/tables/land_use_by_period.csv`).
  - National soybean area cannot detect relocation of soybean or displacement of pasture.

## Layout

```text
analysis/            numbered pipeline (R and Python), run in order by 00_run_all.py
data/processed/      national annual series (forest_loss.csv), CRU climate, IBGE planted area, state outlines
data/derived/        version 2 land-use and exposure-model outputs reused unchanged
results/tables/      every number reported in the manuscript
results/figures/     figures (PDF, PNG, TIFF) and the graphical abstract
manuscript/          data description and the scripts that collect manuscript numbers
archive/             superseded files kept locally for deletion (not committed)
```

| Script | Purpose |
|---|---|
| `13_control_provenance.py` | Download the CRU TS 4.09 annual climate means; compare them with the compiled climate series (runs first) |
| `01_load_data_impute.R` | Build the baseline, response-imputed, and stored-control data sets |
| `02_trade_restructuring.py` | Trade with China, 2001–2024 (descriptive) |
| `03_causal_impact.R` | Baseline and stored-control models in CausalImpact; inclusion probabilities |
| `04_robustness_and_placebos.R` | Trend, control, imputation, start-year, response, MCMC, timing, stored-control, and placebo checks |
| `05_trend_benchmarks.py` | Linear pre-2018 trend benchmarks for MapBiomas and IBGE area |
| `06_land_use_link.py` | Origins and native-cover histories of soybean entry (version 2 accounting) |
| `07_figures.py`, `08_graphical_abstract.py` | Figures 1–4, 6, S1–S4, graphical abstract |
| `09_prepare_state_boundaries.py` | One-off: dissolve IBGE 2024 municipalities to state outlines (output committed) |
| `10_timing_and_political_cycle.R` | Placebos at every year 2008–2017; post-period split and contrast by administration |
| `11_state_map.py` | Figure 5: state maps with legends, scale bar, and north arrow |
| `12_mcmc_diagnostics.R` | Effective sample sizes and Geweke scores; trend models at 2,500 and 10,000 iterations |
| `14_monte_carlo_check.R` | Refits with four independent seeds |
| `manuscript/scripts/ms_numbers.py` | Collects the numbers reported in the manuscript from `results/tables` |

## Reproduce

Requires R ≥ 4.5 and Python ≥ 3.11.

```bash
Rscript analysis/install_r_packages.R   # CausalImpact, bsts, missForest into .runtime/R-library
pip install -r requirements.txt
python analysis/00_run_all.py           # set RSCRIPT if Rscript is not on PATH
```

The manuscript and supplement are kept out of the repository while the paper is under review; every number, table, and figure they report is produced in `results/`.

The run is deterministic: CausalImpact fixes the bsts seed, and every script sets its own seed. Package versions are in `results/sessionInfo.txt`.

## Data

See [data/README.md](data/README.md) for sources, provenance, and the checks applied.

## License

MIT (see `LICENSE`).
