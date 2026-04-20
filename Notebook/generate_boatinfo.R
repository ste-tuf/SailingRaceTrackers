#!/usr/bin/env Rscript

# ============================================================================
# Generate Boat Info - R Script
# Extracts boat metadata from Geovoile configuration XML files
# Converts Python notebook Generate_BoatInfo.ipynb to R
# ============================================================================

# ---- PACKAGES ----

if (!require("xml2", quietly = TRUE)) {
    install.packages("xml2")
    library(xml2)
}

if (!require("jsonlite", quietly = TRUE)) {
    install.packages("jsonlite")
    library(jsonlite)
}

if (!require("tidyverse", quietly = TRUE)) {
    install.packages("tidyverse")
    library(tidyverse)
}

# ---- FUNCTIONS ----

#' Load and parse XML configuration file
#' @param path_file Path to XML config file
#' @return Parsed XML document
load_config <- function(path_file) {
    read_xml(path_file)
}

#' Load and parse JSON report file
#' @param path_file Path to JSON file
#' @return List from JSON
load_report <- function(path_file) {
    json_data <- fromJSON(path_file)
    json_data$reports
}

#' Extract boat information from XML configuration
#' @param config_xml Parsed XML document
#' @return List with boat information indexed by boat ID
extract_boat_info <- function(config_xml) {
    # Navigate to config -> boats -> boat-class -> boat
    boats_node <- xml_find_all(config_xml, ".//boats/boat-class/boat")

    boatinfo_json <- list()

    for (boat_node in boats_node) {
        # Extract boat ID
        boat_id <- as.integer(xml_attr(boat_node, "id"))

        # Extract boat name
        boat_name <- xml_attr(boat_node, "name")

        # Extract category from parent boat-class
        boat_class <- xml_parent(boat_node)
        category <- xml_attr(boat_class, "name")

        # Extract navigators (crew members)
        navigators <- xml_find_all(boat_node, ".//crew/navigator")

        skipper_names <- c()
        for (nav in navigators) {
            fname <- xml_attr(nav, "fname")
            lname <- xml_attr(nav, "lname")
            skipper_names <- c(skipper_names, paste(fname, lname, sep = "_"))
        }

        # Combine skipper names with '_&_' separator
        skipper_combined <- paste(skipper_names, collapse = "_&_")

        # Build boat info entry
        boatinfo_json[[as.character(boat_id)]] <- list(
            boatName = boat_name,
            skipperNames = skipper_combined,
            category = category
        )
    }

    return(boatinfo_json)
}

#' Save boat information to JSON file
#' @param boatinfo List with boat information
#' @param output_file Output JSON file path
save_boatinfo <- function(boatinfo, output_file = "boatinfo.json") {
    write_json(boatinfo, output_file, pretty = TRUE, auto_unbox = TRUE)
}

# ---- MAIN ----

main <- function() {
    cat("=== Generate Boat Info - R Script ===\n\n")

    config_path <- "config.xml"

    if (!file.exists(config_path)) {
        cat("Error: Config file not found:", config_path, "\n")
        cat("Looking for config.xml in current directory...\n")
        config_path <- file.path("..", "config.xml")
        if (!file.exists(config_path)) {
            stop("Config file not found. Please provide a valid XML config file.")
        }
    }

    cat("Loading config from:", config_path, "\n")
    config_xml <- load_config(config_path)

    cat("Extracting boat information...\n")
    boatinfo <- extract_boat_info(config_xml)

    n_boats <- length(boatinfo)
    cat("Extracted information for", n_boats, "boats\n")

    output_file <- "boatinfo.json"
    cat("Saving to:", output_file, "\n")
    save_boatinfo(boatinfo, output_file)

    cat("Done! Boat info saved to", output_file, "\n")

    # Print sample output
    if (n_boats > 0) {
        cat("\nSample output (first boat):\n")
        first_id <- names(boatinfo)[1]
        cat(jsonlite::toJSON(boatinfo[[first_id]], pretty = TRUE))
        cat("\n")
    }
}

# ---- EXECUTE ----

if (!interactive()) {
    main()
}