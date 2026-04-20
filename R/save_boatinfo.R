#' Save boat information to JSON file
#' @param boatinfo List with boat information
#' @param output_file Output JSON file path
save_boatinfo <- function(boatinfo, output_file = "boatinfo.json") {
    write_json(boatinfo, output_file, pretty = TRUE, auto_unbox = TRUE)
}