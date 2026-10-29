# Monte Carlo variation: refit the baseline and the trend specifications with four independent
# bsts and observation-noise seeds. The range across runs shows how much the reported means and
# interval endpoints depend on the simulation; it is not a formal error bound.
source("analysis/00_setup.R")
load("results/intermediate/data_imputed.RData")

specs <- list(
  list(id = "0_baseline", x = CONTROLS, trend = "level"),
  list(id = "2a_local_linear_trend", x = CONTROLS, trend = "local_linear"),
  list(id = "2b_semilocal_trend", x = CONTROLS, trend = "semilocal"),
  list(id = "3c_governance_only_local_linear", x = GOVERNANCE, trend = "local_linear")
)
rows <- list()
for (s in specs) for (k in 1:4) {
  fit <- fit_counterfactual(z_main, RESPONSE, s$x, ORIGINAL$pre, ORIGINAL$post, trend = s$trend,
                            seed = 2025 + k, bsts_seed = k)
  r <- summarise_effect(fit, s$id)
  r$trend <- s$trend; r$chain <- k
  rows[[length(rows) + 1]] <- r
}
mc <- do.call(rbind, rows)
write.csv(mc, "results/tables/mc_seed_check.csv", row.names = FALSE)
print(aggregate(cbind(mean = effect_mean_ha, low = effect_low_ha, high = effect_high_ha) / 1e6 ~ check,
                data = mc, FUN = function(x) round(diff(range(x)), 2)))
