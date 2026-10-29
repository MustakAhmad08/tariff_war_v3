# Baseline BSTS model with CausalImpact, refitted with fit_counterfactual() to validate that
# function. The stored-control specification (compiled smoothed climate, response-informed
# imputation) is also fitted with CausalImpact as a reproduction.
source("analysis/00_setup.R")
load("results/intermediate/data_imputed.RData")

pre <- year_date(ORIGINAL$pre); post <- year_date(ORIGINAL$post)
run_ci <- function(z) {
  set.seed(42)
  CausalImpact(z, pre.period = pre, post.period = post,
    model.args = list(niter = ORIGINAL$niter, standardize.data = TRUE,
      prior.level.sd = ORIGINAL$prior_level_sd, dynamic.regression = FALSE))
}
ci_row <- function(impact, label) {
  s <- impact$summary["Average", ]
  data.frame(check = label, post_start = 2019, post_end = 2024,
    observed_mean_ha = s$Actual, predicted_mean_ha = s$Pred, effect_mean_ha = s$AbsEffect,
    effect_low_ha = s$AbsEffect.lower, effect_high_ha = s$AbsEffect.upper, tail_probability = s$p,
    interval_excludes_zero = s$AbsEffect.lower > 0 | s$AbsEffect.upper < 0)
}
impact <- run_ci(z_main)
stored <- run_ci(z_stored)

fit <- fit_counterfactual(z_main, RESPONSE, CONTROLS, ORIGINAL$pre, ORIGINAL$post)
own <- summarise_effect(fit, "baseline_refit")
own$interval_excludes_zero <- NULL
out <- rbind(ci_row(impact, "baseline_causalimpact"), cbind(own, interval_excludes_zero = own$effect_low_ha > 0 | own$effect_high_ha < 0),
             ci_row(stored, "stored_controls_causalimpact"))
out$summed_annual_deviation_ha <- out$effect_mean_ha * 6
write.csv(out, "results/tables/baseline_model.csv", row.names = FALSE)

series <- annual_series(fit, "baseline")
series$causalimpact_pred_ha <- as.numeric(impact$series$point.pred[as.character(year_date(series$year))])
write.csv(series, "results/tables/baseline_model_series.csv", row.names = FALSE)

coef <- summary(impact$model$bsts.model)$coefficients
inc <- data.frame(variable = rownames(coef), inclusion_probability = coef[, "inc.prob"],
  mean_coefficient = coef[, "mean"])
write.csv(inc[inc$variable != "(Intercept)", ], "results/tables/baseline_inclusion_probabilities.csv",
  row.names = FALSE)
print(out[, c("check", "effect_mean_ha", "effect_low_ha", "effect_high_ha", "tail_probability")])
print(inc)
