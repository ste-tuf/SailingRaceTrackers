#' Extract boat information from XML configuration
#' @param config_xml Parsed XML document
#' @return List with boat information indexed by boat ID
extract_boat_info <- function(config_xml) {
    boats_node <- xml_find_all(config_xml, ".//boats/boatclass/boat")

    boatinfo_json <- list()

    for (boat_node in boats_node) {
        boat_id <- as.integer(xml_attr(boat_node, "id"))
        boat_name <- xml_attr(boat_node, "name")

        boat_class <- xml_parent(boat_node)
        category <- xml_attr(boat_class, "name")

        navigators <- xml_find_all(boat_node, ".//crew/navigator")

        skipper_names <- c()
        for (nav in navigators) {
            fname <- xml_attr(nav, "fname")
            lname <- xml_attr(nav, "lname")
            skipper_names <- c(skipper_names, paste(fname, lname, sep = "_"))
        }

        skipper_combined <- paste(skipper_names, collapse = "_&_")

        boatinfo_json[[as.character(boat_id)]] <- list(
            boatName = boat_name,
            skipperNames = skipper_combined,
            category = category,
            boatClass = xml_attr(boat_node, "comment")
        )
    }

    return(boatinfo_json)
}