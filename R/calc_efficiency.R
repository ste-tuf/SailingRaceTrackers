#' Calculate efficiency (direct distance / actual distance)
#' @param track Matrix or list of (lat, lon) points
#' @return Efficiency ratio (0-1) or NA
calc_efficiency <- function(track) {
    if(is.null(track) || length(track) < 4) return(NA)
    if(is.list(track)) track <- matrix(unlist(track), ncol = 2, byrow = TRUE)
    pts <- track[, 1:2]
    if(nrow(pts) < 2) return(NA)
    actual <- sum(geodist(pts, measure = "haversine", sequential = TRUE)) / 1000 * 0.539957
    direct <- geodist(matrix(c(pts[1, ], pts[nrow(pts), ]), ncol = 2, byrow = TRUE), measure = "haversine")[1] / 1000 * 0.539957
    if(direct < 1) return(NA)
    direct/actual
}