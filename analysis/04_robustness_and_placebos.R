# Robustness checks on the baseline specification. Each check changes one element, except 3c
# and 4b, which change the controls and add a local linear trend, and the stored-control rows,
# which change the climate series and the imputation. Trend specifications use TREND_NITER.
source("analysis/00_setup.R")
load("results/intermediate/data_imputed.RData")

ibge <- read.csv("data/processed/ibge_soy_planted_area_brazil.csv")
z_ibge <- z_main
z_ibge[, RESPONSE] <- ibge$ibge_planted_soy_ha[match(as.integer(format(index(z_ibge), "%Y")), ibge$year)]
stopifnot(!anyNA(z_ibge[, RESPONSE]))

P <- ORIGINAL$pre; Q <- ORIGINAL$post
specs <- list(
  list(id = "0_baseline",             group = "Baseline",          z = z_main, x = CONTROLS, pre = P, post = Q),
  list(id = "2a_local_linear_trend",  group = "Trend",             z = z_main, x = CONTROLS, pre = P, post = Q, trend = "local_linear"),
  list(id = "2b_semilocal_trend",     group = "Trend",             z = z_main, x = CONTROLS, pre = P, post = Q, trend = "semilocal"),
  list(id = "3_climate_controls_only", group = "Controls",         z = z_main, x = CLIMATE,  pre = P, post = Q),
  list(id = "3b_governance_only",     group = "Controls",          z = z_main, x = GOVERNANCE, pre = P, post = Q),
  list(id = "3c_governance_only_local_linear", group = "Controls", z = z_main, x = GOVERNANCE, pre = P, post = Q, trend = "local_linear"),
  list(id = "4a_no_controls",         group = "Controls",          z = z_main, x = character(), pre = P, post = Q),
  list(id = "4b_no_controls_local_linear", group = "Controls",     z = z_main, x = character(), pre = P, post = Q, trend = "local_linear"),
  list(id = "5_impute_with_response", group = "Imputation",        z = z_resp, x = CONTROLS, pre = P, post = Q),
  list(id = "11a_stored_controls",    group = "Stored controls",   z = z_stored, x = CONTROLS, pre = P, post = Q),
  list(id = "11b_stored_controls_local_linear", group = "Stored controls", z = z_stored, x = CONTROLS, pre = P, post = Q, trend = "local_linear"),
  list(id = "6a_start_2001",          group = "Start year",        z = z_main, x = CONTROLS, pre = c(2001, 2018), post = Q),
  list(id = "6b_start_2005",          group = "Start year",        z = z_main, x = CONTROLS, pre = c(2005, 2018), post = Q),
  list(id = "6c_start_2008",          group = "Start year",        z = z_main, x = CONTROLS, pre = c(2008, 2018), post = Q),
  list(id = "8a_ibge_planted_area",   group = "Response",          z = z_ibge, x = CONTROLS, pre = P, post = Q),
  list(id = "8b_ibge_local_linear",   group = "Response",          z = z_ibge, x = CONTROLS, pre = P, post = Q, trend = "local_linear"),
  list(id = "9_niter_10000",          group = "MCMC",              z = z_main, x = CONTROLS, pre = P, post = Q, niter = 10000),
  list(id = "10_post_from_2018",      group = "Timing",            z = z_main, x = CONTROLS, pre = c(2002, 2017), post = c(2018, 2024))
)
# Check 7: placebo interventions before the tariff, four-year post windows ending by 2016.
for (p in 2010:2013) for (tr in c("level", "local_linear")) {
  specs[[length(specs) + 1]] <- list(id = sprintf("7_placebo_%d_%s", p, tr), group = "Placebo",
    z = z_main, x = CONTROLS, pre = c(2002, p - 1), post = c(p, p + 3), trend = tr)
}

rows <- list(); series <- list()
for (s in specs) {
  trend <- if (is.null(s$trend)) "level" else s$trend
  niter <- if (!is.null(s$niter)) s$niter else if (trend == "level") ORIGINAL$niter else TREND_NITER
  fit <- fit_counterfactual(s$z, RESPONSE, s$x, s$pre, s$post, trend = trend, niter = niter)
  r <- summarise_effect(fit, s$id)
  r$group <- s$group; r$trend <- trend; r$controls <- if (length(s$x)) paste(s$x, collapse = ";") else "none"
  r$pre_start <- s$pre[1]; r$pre_end <- s$pre[2]; r$niter <- niter
  rows[[s$id]] <- r
  series[[s$id]] <- annual_series(fit, s$id)
  cat(sprintf("%-32s effect %6.2f Mha [%6.2f, %6.2f] p=%.3f\n", s$id, r$effect_mean_ha / 1e6,
    r$effect_low_ha / 1e6, r$effect_high_ha / 1e6, r$tail_probability))
}
out <- do.call(rbind, rows); rownames(out) <- NULL
write.csv(out, "results/tables/bsts_robustness.csv", row.names = FALSE)
write.csv(do.call(rbind, series), "results/tables/bsts_robustness_series.csv", row.names = FALSE)
writeLines(capture.output(sessionInfo()), "results/sessionInfo.txt")
