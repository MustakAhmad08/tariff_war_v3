# Load data and build the two control sets.
#   z_main      Baseline: stored governance indicators, raw annual CRU TS 4.09 climate
#               (analysis/13), and governance values for 2001 and 2024 imputed without the response.
#               The year enters the imputation table instead, so the imputed values follow the
#               neighbouring years rather than whichever years had similar weather.
#   z_stored    Stored-control specification: the compiled file's smoothed climate series, with
#               governance imputed from a table that includes the response.
#   z_resp      Baseline controls, but governance imputed with the response (imputation check).
source("analysis/00_setup.R")

df <- read.csv("data/processed/forest_loss.csv", check.names = FALSE)
stopifnot(identical(names(df)[c(44, 6:12, 17:19)], c(RESPONSE, CONTROLS)))
df$date <- year_date(df$year)
cru <- read.csv("data/processed/cru_ts409_brazil_annual.csv")
raw <- df
raw[CLIMATE] <- cru[match(df$year, cru$year), CLIMATE]
stopifnot(!anyNA(raw[CLIMATE]))

impute <- function(d, cols) {
  set.seed(42)
  out <- missForest(d[cols], ntree = 500, maxiter = 15)$ximp
  out <- out[setdiff(names(out), "year")]
  zoo(out[c(RESPONSE, CONTROLS)[c(RESPONSE, CONTROLS) %in% cols]], order.by = d$date)
}
with_response <- function(z, d) {
  z <- merge(zoo(d[[RESPONSE]], d$date), z)
  colnames(z) <- c(RESPONSE, CONTROLS)
  z
}
z_main <- with_response(impute(raw, c("year", CONTROLS)), raw)
z_resp <- impute(raw, c(RESPONSE, CONTROLS))
z_stored <- impute(df, c(RESPONSE, CONTROLS))

# The response is never imputed: it has no missing values.
stopifnot(!anyNA(df[[RESPONSE]]))
for (z in list(z_main, z_resp, z_stored))
  stopifnot(all.equal(as.numeric(z[, RESPONSE]), df[[RESPONSE]]), !anyNA(coredata(z)))

missing_years <- df$year[!complete.cases(df[CONTROLS])]
pick <- function(z) as.vector(t(as.matrix(z[year_date(missing_years), GOVERNANCE])))
imputed <- data.frame(
  year = rep(missing_years, each = length(GOVERNANCE)),
  variable = rep(GOVERNANCE, length(missing_years)),
  baseline = pick(z_main), with_response = pick(z_resp), stored_controls = pick(z_stored)
)
write.csv(imputed, "results/tables/imputed_governance_values.csv", row.names = FALSE)

save(df, z_main, z_resp, z_stored, file = "results/intermediate/data_imputed.RData")
cat("Imputed years:", missing_years, "\n")
