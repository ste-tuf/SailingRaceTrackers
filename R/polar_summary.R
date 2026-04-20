#' Summarize polar data
#' @param pd Polar data frame from estimate_polar
#' @param wind Wind direction in degrees
#' @return Summary data frame
polar_summary <- function(pd, wind = NULL) {
    if(is.null(pd) || nrow(pd) < 10) return(NULL)
    if(is.null(wind)) {
        return(data.frame(avg = mean(pd$speed), max = max(pd$speed), min = min(pd$speed), n = nrow(pd)))
    }
    pd <- pd[!is.na(pd$twa) & pd$twa <= 180, ]
    if(nrow(pd) < 10) return(NULL)
    pd$bin <- cut(pd$twa, breaks = c(0,30,45,60,90,120,150,180), labels = c("0-30","30-45","45-60","60-90","90-120","120-150","150-180"), include = TRUE)
    pd %>% group_by(bin) %>% summarise(avg = mean(speed), max = max(speed), n = n(), .groups = "drop")
}