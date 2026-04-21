#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  if (!require("xml2")) install.packages("xml2", repos = "https://cloud.r-project.org")
  if (!require("jsonlite")) install.packages("jsonlite", repos = "https://cloud.r-project.org")
})

library(xml2)
library(jsonlite)
library(targets)
library(here)

tar_source(here("R"))

cat("=== Generate Boat Info - R Script ===\n\n")
config_path <- "data/config.json"

if (!file.exists(config_path)) {
  cat("Error: Config file not found:", config_path, "\n")
  stop("Config file not found. Please provide a valid XML config file.")
}

cat("Loading config from:", config_path, "\n")
config_xml <- load_config(config_path)

cat("Extracting boat information...\n")
boatinfo <- extract_boat_info(config_xml)

n_boats <- length(boatinfo)
cat("Extracted information for", n_boats, "boats\n")

output_file <- "data/boatinfo.json"
cat("Saving to:", output_file, "\n")
save_boatinfo(boatinfo, output_file)

cat("Done! Boat info saved to", output_file, "\n")

if (n_boats > 0) {
  cat("\nSample output (first boat):\n")
  first_id <- names(boatinfo)[1]
  cat(jsonlite::toJSON(boatinfo[[first_id]], pretty = TRUE))
  cat("\n")
}
