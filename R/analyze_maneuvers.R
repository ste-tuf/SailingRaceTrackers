#' Analyze maneuvers (tacks and gybes) in a track
#' @param track Matrix or list of (lat, lon) points
#' @param thresh Threshold angle for maneuver detection
#' @return List with total, tacks, and gybes counts
analyze_maneuvers <- function(track, thresh = 30) {
    if(is.null(track) || length(track) < 10) return(list(total = 0, tacks = 0, gybes = 0))
    if(is.list(track)) track <- matrix(unlist(track), ncol = 2, byrow = TRUE)
    n <- min(nrow(track), 500)
    idx <- seq(1, nrow(track), length.out = n)
    t <- track[idx, ]
    heads <- sapply(2:nrow(t), function(i) calc_heading(t[i-1,1], t[i-1,2], t[i,1], t[i,2]))
    hc <- diff(heads)
    hc <- ifelse(hc > 180, hc - 360, hc)
    hc <- ifelse(hc < -180, hc + 360, hc)
    mi <- which(abs(hc) >= thresh)
    tacks <- sum(hc[mi] < -45)
    gybes <- sum(hc[mi] > 45)
    list(total = length(mi), tacks = tacks, gybes = gybes)
}