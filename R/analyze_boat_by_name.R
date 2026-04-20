#' Find and analyze a boat by name or ID
#' @param target Boat name or ID
#' @param results Results data from boats_result.json
#' @param binfo Boat info from boatinfo.json
#' @param wind Wind direction (optional)
#' @return Analysis results list
analyze_boat_by_name <- function(target, results, binfo, wind = NULL) {
    bd <- NULL; bid <- NULL; bname <- NULL

    if(grepl("^[0-9]+$", target)) {
        ts <- as.integer(target)
        for(id in names(results$result)) {
            if(results$result[[id]]$sail == ts) {
                bd <- results$result[[id]]
                bid <- as.integer(id)
                bname <- binfo[[id]]$boatName
                break
            }
        }
    }
    if(is.null(bd)) {
        for(id in names(binfo)) {
            bn <- binfo[[id]]$boatName
            if(!is.null(bn) && (tolower(bn) == tolower(target) || grepl(target, bn, ignore.case = TRUE))) {
                bid <- as.integer(id)
                bname <- bn
                bd <- results$result[[as.character(bid)]]
                break
            }
        }
    }
    if(is.null(bd)) return(NULL)

    list(
        bid = bid,
        bname = bname,
        bd = bd,
        category = binfo[[as.character(bid)]]$category
    )
}