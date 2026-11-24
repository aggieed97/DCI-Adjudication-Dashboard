"""
DCI Dashboard Data Preparation Script
-------------------------------------
Reads the full `tableau_ready_dci_data.csv` (~130,000 rows), applies caption
name standardization, cleans date formats, and exports two lightweight CSV
files into a `/data` folder optimized for fast loading on GitHub Pages.
"""

import os
import pandas as pd
import numpy as np


def prepare_dashboard_data(input_csv="./data/tableau_ready_dci_data.csv", output_dir="data"):
    """
    Processes the master DCI dataset into two purpose-built, lightweight CSVs:
      1. data/heatmap_data.csv   - Panel-level Kendall's W for double-panel events.
      2. data/bumpchart_data.csv - Slimmed judge vs. consensus rankings.
    """
    if not os.path.exists(input_csv):
        raise FileNotFoundError(
            f"Could not find '{input_csv}'. Make sure it is in the same folder as this script."
        )

    os.makedirs(output_dir, exist_ok=True)
    print(f"Loading {input_csv}...")
    df = pd.read_csv(input_csv)
    original_size_mb = os.path.getsize(input_csv) / (1024 * 1024)

    # 1. Standardize Event Date to clean YYYY-MM-DD (handles mixed 2013-2024 dates and 2025-2026 ISO-Z timestamps)
    try:
        parsed_dates = pd.to_datetime(
            df["eventDate"], format="mixed", utc=True, errors="coerce"
        )
    except ValueError:
        # Fallback for older Pandas versions (< 2.0)
        parsed_dates = pd.to_datetime(df["eventDate"], utc=True, errors="coerce")

    df["eventDate"] = parsed_dates.dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["eventDate", "season", "corpsName", "captionName"])
    df["season"] = df["season"].astype(int)

    # 2. Consolidate duplicate caption names (mirrors the Tableau Grouping step)
    caption_mapping = {
        "Visual Analysis": "Visual - Analysis",
        "Penalties": "Timing & Penalties",
    }
    df["captionName"] = df["captionName"].replace(caption_mapping)

    # Remove experimental/special captions and Timing & Penalties from analytical views
    exclude_mask = df["captionName"].str.startswith("Special", na=False) | (
        df["captionName"] == "Timing & Penalties"
    )
    df = df[~exclude_mask].copy()

    # ---------------------------------------------------------
    # Export 1: Heat Map Data (Only non-null Kendall's W rows)
    # ---------------------------------------------------------
    heatmap_cols = ["season", "eventDate", "eventName", "captionName", "panel_kendall_w"]
    heatmap_df = (
        df.dropna(subset=["panel_kendall_w"])[heatmap_cols]
        .groupby(["season", "eventDate", "eventName", "captionName"], as_index=False)
        .agg({"panel_kendall_w": "mean"})
    )
    heatmap_df["panel_kendall_w"] = heatmap_df["panel_kendall_w"].round(4)
    heatmap_df = heatmap_df.sort_values(["season", "eventDate", "captionName"])

    heatmap_path = os.path.join(output_dir, "heatmap_data.csv")
    heatmap_df.to_csv(heatmap_path, index=False)

    # ---------------------------------------------------------
    # Export 2: Bump Chart Data (Slimmed columns, clean integers)
    # ---------------------------------------------------------
    bump_cols = [
        "season",
        "eventDate",
        "eventName",
        "corpsName",
        "captionName",
        "judgeName",
        "judge_rank",
        "consensus_rank",
    ]
    bump_df = (
        df.dropna(subset=["judge_rank", "consensus_rank", "judgeName"])[bump_cols]
        .groupby(
            ["season", "eventDate", "eventName", "corpsName", "captionName", "judgeName"],
            as_index=False,
        )
        .agg({"judge_rank": "mean", "consensus_rank": "mean"})
    )

    # Round ranks cleanly and compute explicit rank deviation (positive = judge ranked higher/better)
    bump_df["judge_rank"] = bump_df["judge_rank"].round(2)
    bump_df["consensus_rank"] = bump_df["consensus_rank"].round(2)
    bump_df["rank_deviation"] = (bump_df["consensus_rank"] - bump_df["judge_rank"]).round(2)
    bump_df = bump_df.sort_values(["season", "eventDate", "corpsName"])

    bump_path = os.path.join(output_dir, "bumpchart_data.csv")
    bump_df.to_csv(bump_path, index=False)

    # Print summary statistics
    heatmap_kb = os.path.getsize(heatmap_path) / 1024
    bump_mb = os.path.getsize(bump_path) / (1024 * 1024)

    print("\n--- Export Complete ---")
    print(f"Original CSV : {original_size_mb:.2f} MB ({len(df):,} cleaned rows)")
    print(f"Seasons Found: {sorted(df['season'].unique().tolist())}")
    print(f"Heat Map CSV : {heatmap_kb:.1f} KB ({len(heatmap_df):,} rows) -> {heatmap_path}")
    print(f"Bump CSV     : {bump_mb:.2f} MB ({len(bump_df):,} rows) -> {bump_path}")
    print("\nReady to upload 'index.html' and the '/data' folder to GitHub Pages!")


if __name__ == "__main__":
    try:
        prepare_dashboard_data()
    except Exception as exc:
        print(f"Error preparing dashboard data: {exc}")