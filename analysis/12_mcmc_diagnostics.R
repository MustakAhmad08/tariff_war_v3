# MCMC sampling diagnostics for the main BSTS specifications: effective sample size and
# Geweke z-scores for the per-draw average deviation and the variance parameters.
# The estimators follow coda (spectral density at zero from an AR fit, coda::spectrum0.ar;
# Geweke comparison of the first 10% and last 50% of the retained chain), written out here
# because coda is not in the project library. Trend specifications are run with 2,500 and with
# TREND_NITER (10,000) iterations; the reported trend estimates use the longer chains.
source("analysis/00_setup.R")
load("results/intermediate/data_imputed.RData")

spectrum0 <- function(x) {
  if (sd(x) == 0) return(0)
  a <- ar(x, aic = TRUE)
  a$var.pred / (1 - sum(a$ar))^2
}
ess <- function(x) if (sd(x) == 0) NA_real_ else length(x) * var(x) / spectrum0(x)
geweke <- function(x, first = 0.1, last = 0.5) {
  n <- length(x); a <- x[seq_len(floor(first * n))]; b <- x[(n - floor(last * n) + 1):n]
  if (sd(a) == 0 || sd(b) == 0) return(NA_real_)
  (mean(a) - mean(b)) / sqrt(spectrum0(a) / length(a) + spectrum0(b) / length(b))
}

specs <- list(
  list(id = "0_baseline", x = CONTROLS, trend = "level", niter = 2500),
  list(id = "2a_local_linear_trend", x = CONTROLS, trend = "local_linear"),
  list(id = "2b_semilocal_trend", x = CONTROLS, trend = "semilocal"),
  list(id = "3c_governance_only_local_linear", x = GOVERNANCE, trend = "local_linear")
)
for (i in 2:4) { specs[[i]]$niter <- 2500; specs[[length(specs) + 1]] <- modifyList(specs[[i]], list(niter = TREND_NITER)) }
rows <- list()
for (s in specs) {
  niter <- s$niter
  fit <- fit_counterfactual(z_main, RESPONSE, s$x, ORIGINAL$pre, ORIGINAL$post, trend = s$trend, niter = niter)
  eff <- summarise_effect(fit, s$id)
  burn <- SuggestBurn(0.1, fit$model)
  keep <- -seq_len(burn)
  post <- fit$is_post
  chains <- list(average_deviation = rowMeans(sweep(-fit$draws[, post, drop = FALSE], 2, fit$observed[post], "+")))
  params <- grep("^sigma\\.|^trend\\.slope", names(fit$model), value = TRUE)
  for (p in params) chains[[p]] <- fit$model[[p]][keep]
  for (nm in names(chains)) {
    x <- chains[[nm]]
    rows[[length(rows) + 1]] <- data.frame(check = s$id, trend = s$trend, niter = niter,
      effect_mean_ha = eff$effect_mean_ha, effect_low_ha = eff$effect_low_ha,
      effect_high_ha = eff$effect_high_ha, predicted_mean_ha = eff$predicted_mean_ha,
      tail_probability = eff$tail_probability, quantity = nm,
      draws = length(x), ess = ess(x), geweke_z = geweke(x))
  }
}
out <- do.call(rbind, rows)
write.csv(out, "results/tables/mcmc_diagnostics.csv", row.names = FALSE)
print(transform(out[, -1], effect_mean_ha = effect_mean_ha / 1e6, effect_low_ha = effect_low_ha / 1e6,
  effect_high_ha = effect_high_ha / 1e6), digits = 3)
