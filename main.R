#!/usr/bin/env Rscript

# SailingRaceTrackers - Main Entry Point
# Source all functions and run analysis

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


main <- function() {
    cat("=== Boat Analysis ===\n\n")
    cat("Target:", TARGET_BOAT, "\nWind:", WIND_DIR, "deg\n\n")

    results <- fromJSON("../boats_result.json")
    binfo <- fromJSON("boatinfo.json")

    boat_data <- analyze_boat_by_name(TARGET_BOAT, results, binfo)

    if(is.null(boat_data)) {
        cat("Boat not found.\n")
        return()
    }

    bid <- boat_data$bid
    bname <- boat_data$bname
    bd <- boat_data$bd

    cat("\n---", toupper(bname), "---\n")
    cat("Class:", boat_data$category, "\n")
    cat("Rank:", bd$rank, "| Speed:", bd$speed, "kts\n")
    cat("DTF:", bd$dtf, "nm | DTL:", bd$dtl, "nm\n")
    cat("24h:", bd$`24hour_distance`, "nm\n")

    cat("\n--- Track Analysis ---\n")
    tr <- bd$track
    if(!is.null(tr)) {
        if(is.list(tr)) tr <- matrix(unlist(tr), ncol = 2, byrow = TRUE)
        if(is.matrix(tr)) {
            cat("Points:", nrow(tr), "\n")
            man <- analyze_maneuvers(tr)
            cat("Maneuvers:", man$total, "(tacks:", man$tacks, "| gybes:", man$gybes, ")\n")
            eff <- calc_efficiency(tr)
            cat("Efficiency:", round(eff * 100, 1), "%\n")

            cat("\n--- Polar Estimation ---\n")
            pdat <- estimate_polar(tr, WIND_DIR)
            ps <- polar_summary(pdat, WIND_DIR)
            if(!is.null(ps) && nrow(ps) > 0) {
                if(!is.null(ps$bin)) {
                    cat("\nTWA Band | Avg Speed | Max Speed\n")
                    cat("----------|----------|----------\n")
                    for(i in 1:nrow(ps)) cat(sprintf("%-10s| %8.1f | %9.1f\n", as.character(ps$bin[i]), ps$avg[i], ps$max[i]))
                } else {
                    cat("\nOverall: Avg", round(ps$avg, 1), "kts | Max", round(ps$max, 1), "kts\n")
                }
            }
        }
    }
    cat("\n=== Done ===\n")
}

main()
