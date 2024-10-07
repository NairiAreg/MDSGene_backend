import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)

def _count_patients_within_aao_range(
    disease_abbrev: str,
    gene: str,
    aao_range: tuple,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    results = []

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                # Only apply the filter if filter_criteria, country, or mutation is provided
                if filter_criteria is not None or country is not None or mutation is not None:
                    df = apply_filter(df, filter_criteria, None, country, mutation)

                # Filter the dataframe based on the given criteria
                filtered_df = pd.concat(
                    [
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene1"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene2"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene3"] == gene)
                        ],
                    ]
                )

                # Further filter based on clinical status, pathogenicity, and age at onset range
                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity"] != "benign")
                    & (filtered_df["aao"].between(aao_range[0], aao_range[1]))
                ]

                # Get the count of unique patients
                unique_patient_count = filtered_df["patient_id"].nunique()
                results.append(unique_patient_count)

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return sum(results)

def _aao_histogram_missing(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    results = []

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                # Only apply the filter if filter_criteria, aao, or country is provided
                if (
                    filter_criteria is not None
                    or aao is not None
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, country, mutation)

                # Filter the dataframe based on the given criteria
                filtered_df = pd.concat(
                    [
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene1"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene2"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene3"] == gene)
                        ],
                    ]
                )

                # Further filter based on clinical status, pathogenicity, and missing age at onset
                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity"] != "benign")
                    & (filtered_df["aao"].isnull())
                ]

                # Get the count of unique patients
                unique_patient_count = filtered_df["patient_id"].nunique()
                results.append(unique_patient_count)

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return sum(results)

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
    total_eligible = 0

    for interval in aao_intervals:
        nof_patients = _count_patients_within_aao_range(
            disease_abbrev,
            gene,
            (interval.getMinimum(), interval.getMaximum()),
            filter_criteria,
            country,
            mutation,
            directory
        )
        total_patients += nof_patients
        histogram_data.append([f"{interval.getMinimum()} - {interval.getMaximum()}", nof_patients])

    hist_missing = _aao_histogram_missing(
        disease_abbrev,
        gene,
        filter_criteria,
        None,
        country,
        mutation,
        directory
    )

    total_eligible = total_patients + hist_missing
    hist_missing_percentage = (hist_missing * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "histogram_data": histogram_data,
        "total_patients": total_patients,
        "hist_missing_percentage": f"{hist_missing_percentage:.2f}".replace(",", ".")
    }