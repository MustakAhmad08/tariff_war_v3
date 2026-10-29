# Reviewer 2, points 1 and 4-6: does the deviation begin before 2018, and can the
# political cycle be separated from the tariff?
#   (a) Placebo intervention at every year 2008-2017 (windows truncated at 2017).
#   (b) Post-period split: 2019-2022 (Bolsonaro administration) and 2023-2024 (Lula).
# A post-period political indicator cannot enter the model as a control: it is constant
# (zero) throughout the training period, so its coefficient is not identified.
source("analysis/00_setup.R")
load("results/intermediate/data_imputed.RData")

# (a) Placebos at every pre-tariff year.
rows <- list(); series <- list()
for (p in 2008:2017) for (tr in c("level", "local_linear")) {
  post <- c(p, min(p + 3, 2017))
  fit <- fit_counterfactual(z_main, RESPONSE, CONTROLS, c(2002, p - 1), post, trend = tr)
  r <- summarise_effect(fit, sprintf("placebo_%d_%s", p, tr))
  r$placebo_year <- p; r$trend <- tr
  rows[[length(rows) + 1]] <- r
}
pl <- do.call(rbind, rows)
write.csv(pl, "results/tables/placebo_all_years.csv", row.names = FALSE)

# (b) Split the 2019-2024 post-period by administration, using the same fits.
subset_effect <- function(fit, years, label) {
  keep <- fit$is_post & fit$years %in% years
  f <- fit; f$is_post <- keep
  summarise_effect(f, label)
}
# The contrast between administrations uses the same posterior draws for both periods:
# per draw, mean 2023-2024 deviation minus mean 2019-2022 deviation.
period_effect <- function(fit, years) {
  keep <- fit$is_post & fit$years %in% years
  rowMeans(sweep(-fit$draws[, keep, drop = FALSE], 2, fit$observed[keep], "+"))
}
split <- list(); contrast <- list()
for (tr in c("level", "local_linear")) {
  fit <- fit_counterfactual(z_main, RESPONSE, CONTROLS, ORIGINAL$pre, ORIGINAL$post, trend = tr)
  d <- period_effect(fit, 2023:2024) - period_effect(fit, 2019:2022)
  contrast[[tr]] <- data.frame(trend = tr, contrast = "2023-2024 minus 2019-2022",
    difference_mean_ha = mean(d), difference_low_ha = unname(quantile(d, 0.025)),
    difference_high_ha = unname(quantile(d, 0.975)), prob_positive = mean(d > 0))
  for (w in list(list(2019:2024, "2019-2024"), list(2019:2022, "2019-2022 (Bolsonaro)"),
                 list(2023:2024, "2023-2024 (Lula)"))) {
    r <- subset_effect(fit, w[[1]], w[[2]]); r$trend <- tr
    split[[length(split) + 1]] <- r
  }
}
split <- do.call(rbind, split)
write.csv(split, "results/tables/post_period_split.csv", row.names = FALSE)
contrast <- do.call(rbind, contrast); rownames(contrast) <- NULL
write.csv(contrast, "results/tables/post_period_contrast.csv", row.names = FALSE)

fmt <- function(d) cat(sprintf("%-28s %-13s %6.2f [%6.2f, %6.2f] p=%.3f\n", d$check, d$trend,
  d$effect_mean_ha / 1e6, d$effect_low_ha / 1e6, d$effect_high_ha / 1e6, d$tail_probability), sep = "")
fmt(pl); fmt(split); print(contrast)
