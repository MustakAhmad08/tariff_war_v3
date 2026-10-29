# Shared setup: project-local R library, paths, and the original model specification.
lib <- normalizePath(".runtime/R-library", winslash = "/", mustWork = FALSE)
if (dir.exists(lib)) .libPaths(c(lib, .libPaths()))

suppressPackageStartupMessages({
  library(zoo)
  library(dplyr)
  library(missForest)
  library(CausalImpact)
  library(bsts)
})

dir.create("results/tables", recursive = TRUE, showWarnings = FALSE)
dir.create("results/intermediate", recursive = TRUE, showWarnings = FALSE)

# Original specification (tariff_war_forest_loss, analysis/01 and 03).
# Columns 44, 6-12, 17-19 of forest_loss.csv: response, then 10 controls.
RESPONSE <- "FCL_Soybean"  # total mapped soybean area (MapBiomas class 39), ha
GOVERNANCE <- c("econ_free", "cor_con", "gov_eff", "pol_stab", "rule_law", "reg_qual", "voice_acc")
CLIMATE <- c("hum", "prec", "temp")
CONTROLS <- c(GOVERNANCE, CLIMATE)
ORIGINAL <- list(pre = c(2002, 2018), post = c(2019, 2024), niter = 2500, prior_level_sd = 0.15)
# Trend specifications sample slowly at 2,500 iterations (analysis/12), so they use 10,000.
TREND_NITER <- 10000

year_date <- function(y) as.Date(sprintf("%d-01-01", y))

# Fit a BSTS counterfactual the way CausalImpact 1.4.1 does (ConstructModel, pre-period
# standardization, static spike-and-slab regression, bsts seed 1, trajectories with
# observation noise), but allow the trend component to change. bsts_seed and seed can be varied
# to measure Monte Carlo error; the defaults reproduce every reported run. Returns per-draw
# post-period trajectories in hectares.
fit_counterfactual <- function(z, response, controls, pre, post, trend = "level",
                               niter = if (trend == "level") ORIGINAL$niter else TREND_NITER,
                               prior_level_sd = ORIGINAL$prior_level_sd,
                               seed = 2026, bsts_seed = 1) {
  years <- as.integer(format(index(z), "%Y"))
  keep <- years >= pre[1] & years <= post[2]
  z <- z[keep]; years <- years[keep]
  is_pre <- years <= pre[2]
  is_post <- years >= post[1]
  data <- as.data.frame(coredata(z[, c(response, controls), drop = FALSE]))
  names(data) <- make.names(names(data))
  mu <- sapply(data, function(x) mean(x[is_pre])); s <- sapply(data, function(x) sd(x[is_pre]))
  std <- as.data.frame(Map(function(x, m, d) (x - m) / d, data, mu, s))
  y_obs <- data[[1]]
  y <- std[[1]]; y[!is_pre] <- NA  # Also masks any gap years between pre and post.
  sdy <- sd(y, na.rm = TRUE)
  level_prior <- SdPrior(sigma.guess = prior_level_sd * sdy, upper.limit = sdy, sample.size = 32)
  ss <- switch(trend,
    level = AddLocalLevel(list(), y, sigma.prior = level_prior),
    local_linear = AddLocalLinearTrend(list(), y, level.sigma.prior = level_prior),
    semilocal = AddSemilocalLinearTrend(list(), y, level.sigma.prior = level_prior),
    stop("Unknown trend: ", trend))
  if (length(controls)) {
    std[[1]] <- y
    model <- bsts(as.formula(paste(names(std)[1], "~ .")), data = std, state.specification = ss,
      expected.model.size = 3, expected.r2 = 0.8, prior.df = 50, niter = niter,
      seed = bsts_seed, ping = 0, model.options = BstsOptions(save.prediction.errors = TRUE))
  } else {
    model <- bsts(y, state.specification = ss, niter = niter, seed = bsts_seed, ping = 0,
      model.options = BstsOptions(save.prediction.errors = TRUE))
  }
  burn <- SuggestBurn(0.1, model)
  states <- colSums(aperm(model$state.contributions[-seq_len(burn), , , drop = FALSE], c(2, 1, 3)))
  set.seed(seed)
  sigma <- model$sigma.obs[-seq_len(burn)]
  draws <- states + matrix(rnorm(length(states), 0, sigma), nrow = nrow(states))
  draws <- draws * s[1] + mu[1]
  list(model = model, years = years, observed = y_obs, draws = draws,
       is_pre = is_pre, is_post = is_post)
}

# CausalImpact-style summary of the average post-period effect, in hectares.
summarise_effect <- function(fit, label) {
  post <- fit$is_post
  obs <- fit$observed[post]
  pred <- fit$draws[, post, drop = FALSE]
  eff <- rowMeans(sweep(-pred, 2, obs, "+"))
  sum_pred <- rowSums(pred); sum_obs <- sum(obs)
  p <- min(sum(c(sum_pred, sum_obs) >= sum_obs), sum(c(sum_pred, sum_obs) <= sum_obs)) /
    (length(sum_pred) + 1)
  data.frame(check = label, post_start = min(fit$years[post]), post_end = max(fit$years[post]),
    observed_mean_ha = mean(obs), predicted_mean_ha = mean(rowMeans(pred)),
    effect_mean_ha = mean(eff), effect_low_ha = unname(quantile(eff, 0.025)),
    effect_high_ha = unname(quantile(eff, 0.975)), tail_probability = p,
    interval_excludes_zero = unname(quantile(eff, 0.025) > 0 | quantile(eff, 0.975) < 0))
}

# Annual observed, mean prediction and 95% interval for figures.
annual_series <- function(fit, label) {
  data.frame(check = label, year = fit$years, observed_ha = fit$observed,
    predicted_ha = colMeans(fit$draws), predicted_low_ha = apply(fit$draws, 2, quantile, 0.025),
    predicted_high_ha = apply(fit$draws, 2, quantile, 0.975),
    period = ifelse(fit$is_pre, "pre", ifelse(fit$is_post, "post", "gap")))
}
