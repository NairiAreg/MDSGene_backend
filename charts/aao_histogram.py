import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter
from scipy.stats import describe
import numpy as np

logger = logging.getLogger(__name__)


def _fetch_aao_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    aao_data = []

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                logger.info(
                    f"Processing file: {filename}, Initial DataFrame shape: {df.shape}"
                )

                # Safely filter based on ensemble_decision
                if "ensemble_decision" in df.columns:
                    df = df[df["ensemble_decision"] == "IN"]
                logger.info(f"After ensemble_decision filter: {df.shape}")

                # Only apply the filter if filter_criteria, country, or mutation is provided
                if (
                    filter_criteria is not None
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, None, country, mutation)
                logger.info(f"After apply_filter: {df.shape}")

                # Safely filter based on disease_abbrev and gene
                disease_mask = (
                    df["disease_abbrev"] == disease_abbrev
                    if "disease_abbrev" in df.columns
                    else pd.Series(True, index=df.index)
                )
                gene_mask = (
                    (df["gene1"] == gene)
                    | (df["gene2"] == gene)
                    | (df["gene3"] == gene)
                )
                filtered_df = df[disease_mask & gene_mask]
                logger.info(
                    f"After disease_abbrev and gene filter: {filtered_df.shape}"
                )

                # Safely apply additional filters
                status_mask = (
                    filtered_df["status_clinical"] != "clinically unaffected"
                    if "status_clinical" in filtered_df.columns
                    else pd.Series(True, index=filtered_df.index)
                )
                pathogenicity_mask = (
                    (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                )
                aao_mask = (
                    (filtered_df["aao"].notnull() & (filtered_df["aao"] != -99))
                    if "aao" in filtered_df.columns
                    else pd.Series(True, index=filtered_df.index)
                )

                filtered_df = filtered_df[status_mask & pathogenicity_mask & aao_mask]
                logger.info(f"After additional filters: {filtered_df.shape}")

                # Collect age at onset data
                if "aao" in filtered_df.columns:
                    aao_data.extend(filtered_df["aao"].dropna().tolist())

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue

    logger.info(f"Total aao_data points: {len(aao_data)}")
    return aao_data


def generate_aao_histogram(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    aao_data = _fetch_aao_data(
        disease_abbrev, gene, filter_criteria, country, mutation, directory
    )

    # Remove any remaining -99 values
    aao_data = [x for x in aao_data if x != -99]

    if not aao_data:
        logger.warning(
            f"No valid data found for disease_abbrev: {disease_abbrev}, gene: {gene}"
        )
        return None

    aao_data.sort()
    stats_by_years = describe(aao_data)

    # Check if we have enough data points for percentiles
    if len(aao_data) >= 4:
        percentiles = np.percentile(aao_data, [25, 50, 75])
        hist_aao_25_percent = round(percentiles[0], 2)
        hist_aao_median = round(percentiles[1], 2)
        hist_aao_75_percent = round(percentiles[2], 2)
    else:
        hist_aao_25_percent = hist_aao_median = hist_aao_75_percent = None

    # Group the aao_data into age ranges
    grouped_data = [0] * 10  # Initialize with 10 groups (0-9, 10-19, ..., 90-99)

    for age in aao_data:
        if 0 <= age <= 99:
            group_index = int(age // 10)
            grouped_data[group_index] += 1

    chart_config = {
        "accessibility": {
            "enabled": False,
        },
        "chart": {"type": "column"},
        "title": {"text": "Distribution of age at onset"},
        "subtitle": {
            "text": f"Median: {hist_aao_median}; 25th/75th perc.: {hist_aao_25_percent}/{hist_aao_75_percent}; Range: {stats_by_years.minmax[0]:.2f}-{stats_by_years.minmax[1]:.2f} yrs."
        },
        "xAxis": {
            "categories": [
                "0 - 9",
                "10 - 19",
                "20 - 29",
                "30 - 39",
                "40 - 49",
                "50 - 59",
                "60 - 69",
                "70 - 79",
                "80 - 89",
                "90 - 99",
            ],
            "title": {"text": "Age at onset"},
        },
        "yAxis": {
            "title": {"text": "Number of patients"},
            "min": 0,
            "max": max(grouped_data)
            + 50
            - (max(grouped_data) % 50),  # Round up to nearest 50
            "tickInterval": 50,
        },
        "plotOptions": {
            "column": {
                "color": "#AC202D",
                "groupPadding": 0,
                "pointPadding": 0,
                "borderWidth": 0,
            }
        },
        "tooltip": {
            "headerFormat": "{point.key}<br>",
            "pointFormat": "<b>{point.y}</b>Patients",
            "hideDelay": 0,
            "shared": True,
            "useHTML": True,
        },
        "series": [{"name": "Age distribution", "data": grouped_data}],
        "credits": {"enabled": False},
        "legend": {"enabled": False},
    }

    return chart_config
