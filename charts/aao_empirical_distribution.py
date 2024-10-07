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
                    filtered_df["aao"].notnull()
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


def generate_aao_empirical_distribution(
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

    if not aao_data:
        logger.warning(
            f"No data found for disease_abbrev: {disease_abbrev}, gene: {gene}"
        )
        return None

    aao_data.sort()
    stats_by_years = describe(aao_data)

    if len(aao_data) >= 4:
        percentiles = np.percentile(aao_data, [25, 50, 75])
        hist_aao_25_percent = round(percentiles[0], 2)
        hist_aao_median = round(percentiles[1], 2)
        hist_aao_75_percent = round(percentiles[2], 2)
    else:
        hist_aao_25_percent = hist_aao_median = hist_aao_75_percent = None

    histogram_data = []
    start_from_0years = [0, 0]
    histogram_data.append(start_from_0years)
    prev = start_from_0years
    prev_value = -1

    for x in aao_data:
        if prev_value < x:
            prev_value = x
        else:
            continue
        if not (0.0 <= x <= 99.9):
            continue
        pp = (sum(1 for a in aao_data if a <= x) * 100.0) / len(aao_data)
        histogram_data.append([x, prev[1]])
        histogram_data.append([x + 0.1, round(pp, 2)])
        prev = [x + 0.1, round(pp, 2)]

    histogram_data.append([100, prev[1]])

    return {
        "hist_aao_ed_data": histogram_data,
        "hist_aao_25_percent": hist_aao_25_percent,
        "hist_aao_75_percent": hist_aao_75_percent,
        "hist_aao_median": hist_aao_median,
        "hist_range_min_years": (
            stats_by_years.minmax[0] if hasattr(stats_by_years, "minmax") else None
        ),
        "hist_range_max_years": (
            stats_by_years.minmax[1] if hasattr(stats_by_years, "minmax") else None
        ),
    }
