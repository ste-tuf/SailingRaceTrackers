#' Load and parse XML configuration file
#' @param path_file Path to XML config file
#' @return Parsed XML document
load_config <- function(path_file) {
    read_xml(path_file)
}