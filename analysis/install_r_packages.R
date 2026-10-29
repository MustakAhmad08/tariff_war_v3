# Install the R packages into the ignored project library: Rscript analysis/install_r_packages.R
dir.create(".runtime/R-library", recursive = TRUE, showWarnings = FALSE)
lib <- normalizePath('.runtime/R-library', winslash='/', mustWork=TRUE)
.libPaths(c(lib, .libPaths()))
pk <- c('CausalImpact','bsts','missForest','zoo','dplyr','ggplot2')
need <- pk[!vapply(pk, requireNamespace, logical(1), quietly=TRUE)]
if (length(need)) install.packages(need, lib=lib, repos='https://cloud.r-project.org')
for (p in pk) cat(p, as.character(packageVersion(p, lib.loc=c(lib,.libPaths()))), '\n')
