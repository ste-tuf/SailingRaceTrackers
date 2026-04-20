#!/usr/bin/env Rscript
# Analyze Boat Performance

suppressPackageStartupMessages({
    if (!require("geodist")) install.packages("geodist", repos="https://cloud.r-project.org")
    if (!require("jsonlite")) install.packages("jsonlite", repos="https://cloud.r-project.org")
    if (!require("tidyverse")) install.packages("tidyverse", repos="https://cloud.r-project.org")
})
library(geodist)
library(jsonlite)
library(tidyverse)
options(digits=3, warn=FALSE)

# Configuration
TARGET_BOAT <- "Actual Ultim 4"
WIND_DIR <- 270

# Functions
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

analyze_maneuvers <- function(track, thresh=30) {
    if(is.null(track) || length(track) < 10) return(list(total=0, tacks=0, gybes=0))
    if(is.list(track)) track <- matrix(unlist(track), ncol=2, byrow=TRUE)
    n <- min(nrow(track), 500)
    idx <- seq(1, nrow(track), length.out=n)
    t <- track[idx,]
    heads <- sapply(2:nrow(t), function(i) calc_heading(t[i-1,1], t[i-1,2], t[i,1], t[i,2]))
    hc <- diff(heads)
    hc <- ifelse(hc > 180, hc - 360, hc)
    hc <- ifelse(hc < -180, hc + 360, hc)
    mi <- which(abs(hc) >= thresh)
    tacks <- sum(hc[mi] < -45)
    gybes <- sum(hc[mi] > 45)
    list(total=length(mi), tacks=tacks, gybes=gybes)
}

calc_efficiency <- function(track) {
    if(is.null(track) || length(track) < 4) return(NA)
    if(is.list(track)) track <- matrix(unlist(track), ncol=2, byrow=TRUE)
    pts <- track[,1:2]
    if(nrow(pts) < 2) return(NA)
    actual <- sum(geodist(pts, measure="haversine", sequential=TRUE)) / 1000 * 0.539957
    direct <- geodist(matrix(c(pts[1,], pts[nrow(pts),]), ncol=2, byrow=TRUE), measure="haversine")[1] / 1000 * 0.539957
    if(direct < 1) return(NA)
    direct/actual
}

estimate_polar <- function(track, wind=NULL) {
    if(is.null(track) || length(track) < 50) return(NULL)
    if(is.list(track)) track <- matrix(unlist(track), ncol=2, byrow=TRUE)
    n <- min(nrow(track), 300)
    idx <- seq(1, nrow(track), length.out=n)
    t <- track[idx,]
    pd <- data.frame(speed=numeric(), twa=numeric())
    for(i in 2:(nrow(t)-1)) {
        d <- geodist(matrix(c(t[i-1,], t[i,]), ncol=2, byrow=TRUE), measure="haversine", sequential=TRUE)[1]
        spd <- (d/1000) * 0.539957
        if(spd > 2 && spd < 25) {
            h <- calc_heading(t[i-1,1], t[i-1,2], t[i,1], t[i,2])
            if(!is.null(wind)) {
                tw <- abs(h - wind)
                tw <- min(tw, 360-tw)
            } else tw <- NA
            pd <- rbind(pd, data.frame(speed=spd, twa=tw))
        }
    }
    pd
}

polar_summary <- function(pd, wind=NULL) {
    if(is.null(pd) || nrow(pd) < 10) return(NULL)
    if(is.null(wind)) {
        return(data.frame(avg=mean(pd$speed), max=max(pd$speed), min=min(pd$speed), n=nrow(pd)))
    }
    pd <- pd[!is.na(pd$twa) & pd$twa <= 180,]
    if(nrow(pd) < 10) return(NULL)
    pd$bin <- cut(pd$twa, breaks=c(0,30,45,60,90,120,150,180), labels=c("0-30","30-45","45-60","60-90","90-120","120-150","150-180"), include=TRUE)
    pd %>% group_by(bin) %>% summarise(avg=mean(speed), max=max(speed), n=n(), .groups="drop")
}

# Main
main <- function() {
    cat("=== Boat Analysis ===\n\n")
    cat("Target:", TARGET_BOAT, "\nWind:", WIND_DIR, "deg\n\n")
    
    results <- fromJSON("../boats_result.json")
    binfo <- fromJSON("boatinfo.json")
    
    bd <- NULL; bid <- NULL; bname <- NULL
    
    if(grepl("^[0-9]+$", TARGET_BOAT)) {
        ts <- as.integer(TARGET_BOAT)
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
            if(!is.null(bn) && (tolower(bn)==tolower(TARGET_BOAT) || grepl(TARGET_BOAT, bn, ignore=TRUE))) {
                bid <- as.integer(id)
                bname <- bn
                bd <- results$result[[as.character(bid)]]
                cat("Found:", bn, "(ID:", bid, ")\n")
                break
            }
        }
    }
    if(is.null(bd)) { cat("Boat not found.\n"); return() }
    
    cat("\n---", toupper(bname), "---\n")
    cat("Class:", binfo[[as.character(bid)]]$category, "\n")
    cat("Rank:", bd$rank, "| Speed:", bd$speed, "kts\n")
    cat("DTF:", bd$dtf, "nm | DTL:", bd$dtl, "nm\n")
    cat("24h:", bd$`24hour_distance`, "nm\n")
    
    cat("\n--- Track Analysis ---\n")
    tr <- bd$track
    if(!is.null(tr)) {
        if(is.list(tr)) tr <- matrix(unlist(tr), ncol=2, byrow=TRUE)
        if(is.matrix(tr)) {
            cat("Points:", nrow(tr), "\n")
            man <- analyze_maneuvers(tr)
            cat("Maneuvers:", man$total, "(tacks:", man$tacks, "| gybes:", man$gybes, ")\n")
            eff <- calc_efficiency(tr)
            cat("Efficiency:", round(eff*100,1), "%\n")
            
            cat("\n--- Polar Estimation ---\n")
            pdat <- estimate_polar(tr, WIND_DIR)
            ps <- polar_summary(pdat, WIND_DIR)
            if(!is.null(ps) && nrow(ps) > 0) {
                if(!is.null(ps$bin)) {
                    cat("\nTWA Band | Avg Speed | Max Speed\n")
                    cat("----------|----------|----------\n")
                    for(i in 1:nrow(ps)) cat(sprintf("%-10s| %8.1f | %9.1f\n", as.character(ps$bin[i]), ps$avg[i], ps$max[i]))
                } else {
                    cat("\nOverall: Avg", round(ps$avg,1), "kts | Max", round(ps$max,1), "kts\n")
                }
            }
        }
    }
    cat("\n=== Done ===\n")
}
main()
