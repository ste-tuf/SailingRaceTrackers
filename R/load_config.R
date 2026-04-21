#' Load and parse XML configuration file
#' @param path_file Path to XML config file
#' @return Parsed XML document
load_config <- function(path_file) {
    xml_content <- readLines(path_file, encoding = "UTF-8", warn = FALSE)
    xml_content <- paste(xml_content, collapse = "\n")
    read_xml(xml_content)
}