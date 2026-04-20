#' Calculate heading between two points
#' @param lat1 Latitude of point 1
#' @param lon1 Longitude of point 1
#' @param lat2 Latitude of point 2
#' @param lon2 Longitude of point 2
#' @return Heading in degrees
calc_heading <- function(lat1, lon1, lat2, lon2) {
    lat1r <- lat1 * pi/180
    lat2r <- lat2 * pi/180
    dlonr <- (lon2 - lon1) * pi/180
    y <- sin(dlonr) * cos(lat2r)
    x <- cos(lat1r) * sin(lat2r) - sin(lat1r) * cos(lat2r) * cos(dlonr)
    h <- atan2(y, x) * 180/pi
    if(h < 0) h <- h + 360
    h
}