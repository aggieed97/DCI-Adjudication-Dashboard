# DCI Judging Volatility & Ordinal Dissent Dashboard

An interactive web dashboard analyzing panel-wide adjudication agreement and individual judge rank deviations across Drum Corps International (DCI) competitive seasons (2013–2026).

**Live Dashboard:** `https://aggieed97.github.io/DCI-Adjudication-Dashboard/`

---

## Overview

In competitive marching arts, judging panels expand from single adjudicators during weekday tour events to double panels at major regionals and World Championships. This project quantifies **ordinal dissent** across 14 seasons of DCI recap data using two complementary views:

1. **Panel Volatility Heat Map (Kendall's $W$):** Measures panel-wide concordance on a numerical scale ($0.000$ = complete dissent, $1.000$ = perfect agreement). Single-judge captions where $W$ is mathematically undefined are explicitly marked `N/A`.
2. **Ordinal Dissent Bump Chart:** Compares the **Panel Consensus Rank** (solid lines styled in official DCI corps hex colors with direct end-of-line labels) against an **Individual Adjudicator's Rank** (white-centered ringed dots), with toggleable dotted dissent whiskers.

---

## Interactive Features

* **Global Season Selector & KPI Strip:** Dynamically updates both charts and summarizes the season's average Kendall's $W$, most volatile caption, and peak dissent event.
* **Cross-Filtering:** Clicking any colored tile on the Heat Map highlights that event on the Bump Chart below and filters to the corresponding caption.
* **Adjudicator & Corps Filtering:** Compare specific judges and toggle individual corps chips on or off to isolate ranking disagreements.
* **Client-Side CSV Loader:** Includes a **Load Your CSV** button for testing custom or updated datasets directly in the browser.

---

## Repository Structure

```text
├── index.html                 # Self-contained Plotly.js + Tailwind CSS dashboard
├── prep_dashboard_data.py     # Python script to clean and slim raw DCI data for web hosting
├── data/
│   ├── heatmap_data.csv       # Aggregated panel-level Kendall's W scores
│   └── bumpchart_data.csv     # Standardized judge vs. consensus rank records
└── .gitignore                 # Excludes local virtual environments and raw master CSV
```

---

## Data Pipeline & Local Usage

To regenerate the lightweight `/data` files from the full master dataset (`tableau_ready_dci_data.csv`, ~130,000 rows):

1. Place `tableau_ready_dci_data.csv` in the data directory.
2. Run the data preparation script:
   ```bash
   python prep_dashboard_data.py
   ```
   This script standardizes mixed 2013–2026 date formats, consolidates duplicate caption names (e.g., *Visual Analysis* → *Visual - Analysis*), filters out experimental/special captions, and exports the optimized CSVs into `/data`.

---

## Tech Stack

* **Visualization & UI:** Plotly.js, Tailwind CSS, PapaParse
* **Data Processing:** Python, Pandas, NumPy
* **Hosting:** GitHub Pages