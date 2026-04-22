# SailingRaceTrackers - Agent Instructions

## Quick Start
```bash
npm install
node download-reports.js
node generate-result.js
```

## Key Commands
- `npm install` - Install Node.js dependencies (axios, jsdom)
- `node download-reports.js` - Fetch data from Geovoile (requires internet)
- `node generate-result.js` - Process data into `boats_result.json`

## Project Structure
- `download-reports.js` - Fetches and decodes binary `.hwx` files from Geovoile
- `generate-result.js` - Converts raw data to structured JSON with tracks
- `config.json` - Race configuration (route, boats, classes)
- `boats.json` / `tracks.json` / `boats_result.json` - Generated data files
- `qmd/*.qmd` - Quarto reports for generating race analysis

## Important Notes
- Each race has its own branch (`prod-*`). The active branch appears in `.github/workflows/generate-boats-result-template.yml`
- The GitHub workflow auto-updates data: `npm ci` → `node download-reports.js` → `node generate-result.js`
- Known issue: `generate-result.js` uses a hardcoded array index (31) for GPS track data that may vary per race - see README line 431

## Generated Output Format (boats_result.json)
```json
{
  "result": {
    "123": {
      "sail": 123, "rank": 1, "heading": 245, "speed": 18.5,
      "lat_dec": 46.275, "lon_dec": -1.475,
      "dtf": 1234.5, "dtl": 0.0, "dtp": 45.2,
      "track": [[lat, lon], ...]
    }
  }
}
```

## Report Generation
- Run Quarto to generate reports: `quarto render qmd/race_report.qmd`
- Computation times are tracked in `computation_times.txt`
- Report sections: Current status/ranking, time trends (since last computation, last 4h, last 24h)
