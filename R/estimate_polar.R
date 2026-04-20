#' Estimate polar data from track
#' @param track Matrix or list of (lat, lon) points
#' @param wind Wind direction in degrees
#' @return Data frame with speed and TWA columns
estimate_polar <- function(track, wind = NULL) {
    if(is.null(track) || length(track) < 50) return(NULL)
    if(is.list(track)) track <- matrix(unlist(track), ncol = 2, byrow = TRUE)
    n <- min(nrow(track), 300)
    idx <- seq(1, nrow(track), length.out = n)
    t <- track[idx, ]
    pd <- data.frame(speed = numeric(), twa = numeric())
    for(i in 2:(nrow(t)-1)) {
        d <- geodist(matrix(c(t[i-1, ], t[i, ]), ncol = 2, byrow = TRUE), measure = "haversine", sequential = TRUE)[1]
        spd <- (d/1000) * 0.539957
        if(spd > 2 && spd < 25) {
            h <- calc_heading(t[i-1,1], t[i-1,2], t[i,1], t[i,2])
            if(!is.null(wind)) {
                tw <- abs(h - wind)
                tw <- min(tw, 360-tw)
            } else tw <- NA
            pd <- rbind(pd, data.frame(speed = spd, twa = tw))
        }
    }
    pd
}