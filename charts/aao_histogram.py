import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)

def _fetch_aao_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
    include_missing: bool = False
):
    disease_abbrev = disease_abbrev
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
                if not include_missing:
                    aao_mask = (
                        (filtered_df["aao"].notnull() & (filtered_df["aao"] != -99))
                        if "aao" in filtered_df.columns
                        else pd.Series(True, index=filtered_df.index)
                    )
                else:
                    aao_mask = pd.Series(True, index=filtered_df.index)

                filtered_df = filtered_df[status_mask & pathogenicity_mask & aao_mask]
                logger.info(f"After additional filters: {filtered_df.shape}")

                # Collect age at onset data
                if "aao" in filtered_df.columns:
                    aao_data.extend(filtered_df["aao"].tolist())

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue

    logger.info(f"Total aao_data points: {len(aao_data)}")
    return aao_data

def _count_patients_within_aao_range(
    disease_abbrev: str,
    gene: str,
    aao_range: tuple,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    aao_data = _fetch_aao_data(disease_abbrev, gene, filter_criteria, country, mutation, directory)
    count = sum(1 for aao in aao_data if pd.notna(aao) and aao_range[0] <= aao <= aao_range[1])
    return count

def _aao_histogram_missing(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    aao_data = _fetch_aao_data(disease_abbrev, gene, filter_criteria, country, mutation, directory, include_missing=True)
    count = sum(1 for aao in aao_data if pd.isna(aao) or aao == -99)
    return count

def generate_aao_histogram(
    disease_abbrev: str,
    gene: str,
    aao_intervals: list,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    histogram_data = []
    total_patients = 0

    for interval in aao_intervals:
        nof_patients = _count_patients_within_aao_range(
            disease_abbrev,
            gene,
            (interval, interval + 9),
            filter_criteria,
            country,
            mutation,
            directory
        )
        total_patients += nof_patients
        histogram_data.append([f"{interval} - {interval + 9}", nof_patients])

    hist_missing = _aao_histogram_missing(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    total_eligible = total_patients + hist_missing
    hist_missing_percentage = (hist_missing * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "chart": {"type": "column"},
        "title": {"text": "Age at Onset Histogram"},
        "subtitle": {
            "text": f"Number of patients with missing data: {hist_missing} ({hist_missing_percentage}%)"
        },
        "xAxis": {"categories": [interval[0] for interval in histogram_data], "title": {"text": "Age at Onset"}},
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "series": [
            {"name": "Patients", "data": [interval[1] for interval in histogram_data], "color": "#A52A2A"}
            # Dark red color
        ],
    }