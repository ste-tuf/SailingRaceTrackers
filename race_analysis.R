#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  if (!require("gt")) install.packages("gt", repos = "https://cloud.r-project.org")
  if (!require("jsonlite")) install.packages("jsonlite", repos = "https://cloud.r-project.org")
  if (!require("dplyr")) install.packages("dplyr", repos = "https://cloud.r-project.org")
})

library(gt)
library(jsonlite)
library(dplyr)

TARGET_BOAT <- "TUF TUF TUF Coeur en liberté"
WIND_DIR <- 75

results <- fromJSON("boats.json")
binfo <- fromJSON("boatinfo.json")

process_results <- function(results, binfo) {
  history <- results$reports$history
  if (is.null(history) || nrow(history) == 0) {
    return(data.frame())
  }

  latest <- history[nrow(history), ]
  lines <- latest$lines[[1]]

  df <- do.call(rbind, lapply(lines, function(x) {
    data.frame(
      boat = as.integer(x[[1]]),
      rank = as.integer(x[[3]]),
      speed = as.numeric(x[[9]]),
      vmg = as.numeric(x[[10]]),
      dtf = as.numeric(x[[5]]),
      dtl = as.numeric(x[[6]]),
      stringsAsFactors = FALSE
    )
  }))

  df <- df %>%
    left_join(
      data.frame(
        boat = as.integer(names(binfo)),
        boatName = sapply(binfo, function(x) x$boatName),
        category = sapply(binfo, function(x) x$category),
        boatClass = sapply(binfo, function(x) x$boatClass),
        skipperNames = sapply(binfo, function(x) x$skipperNames) |>
          str_replace("_", " ")
      ),
      by = "boat"
    )

  return(df)
}

results_df <- process_results(results, binfo)

saveRDS(results_df, "results_df.rds")
saveRDS(list(target = TARGET_BOAT, wind = WIND_DIR), "params.rds")
