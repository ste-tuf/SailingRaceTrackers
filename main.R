#!/usr/bin/env Rscript

# SailingRaceTrackers - Main Entry Point
# Generates data for Quarto report

suppressPackageStartupMessages({
    if (!require("geodist")) install.packages("geodist", repos = "https://cloud.r-project.org")
    if (!require("jsonlite")) install.packages("jsonlite", repos = "https://cloud.r-project.org")
    if (!require("tidyverse")) install.packages("tidyverse", repos = "https://cloud.r-project.org")
    if (!require("xml2")) install.packages("xml2", repos = "https://cloud.r-project.org")
})

library(geodist)
library(jsonlite)
library(tidyverse)
library(xml2)
library(targets)
library(here)

options(digits = 3, warn = FALSE)

tar_source(here("R"))

TARGET_BOAT <- "TUF TUF TUF Coeur en liberté"
WIND_DIR <- 75

main <- function() {
    results <- fromJSON("boats_result.json")

    if(is.null(results$result) || length(results$result) == 0) {
        results <- fromJSON("boats.json")
    }

    if(!file.exists("boatinfo.json")) {
        cat("Generating boatinfo.json...\n")
        config_xml <- load_config("config.json")
        boatinfo <- extract_boat_info(config_xml)
        save_boatinfo(boatinfo, "boatinfo.json")
    }

    binfo <- fromJSON("boatinfo.json")

    process_results <- function(results, binfo) {
        history <- results$reports$history
        if(is.null(history) || nrow(history) == 0) return(data.frame())

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
                    skipperNames = sapply(binfo, function(x) x$skipperNames)
                ),
                by = "boat"
            )

        return(df)
    }

    results_df <- process_results(results, binfo)

    saveRDS(results_df, "results_df.rds")
    saveRDS(list(target = TARGET_BOAT, wind = WIND_DIR), "params.rds")

    cat("Data saved. Run 'quarto render qmd/race_report.qmd' to generate report.\n")
}

main()
