import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)

def _fetch_signs_and_symptoms(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    symptoms_data = {}

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                if filter_criteria is not None or country is not None or mutation is not None:
                    df = apply_filter(df, filter_criteria, None, country, mutation)

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

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity"] != "benign")
                ]

                for column in filtered_df.columns:
                    if column.endswith("_sympt") or "_hp:" in column:
                        symptom_counts = filtered_df[column].value_counts().to_dict()
                        symptoms_data.update(symptom_counts)

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return symptoms_data

def _fetch_signs_and_symptoms_missing(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    missing_count = 0

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                if filter_criteria is not None or country is not None or mutation is not None:
                    df = apply_filter(df, filter_criteria, None, country, mutation)

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

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity"] != "benign")
                ]

                for column in filtered_df.columns:
                    if column.endswith("_sympt") or "_hp:" in column:
                        missing_count += filtered_df[column].isnull().sum()

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return missing_count

def generate_signs_and_symptoms(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    symptoms_data = _fetch_signs_and_symptoms(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    signs_and_symptoms_missing = _fetch_signs_and_symptoms_missing(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    total_eligible = sum(symptoms_data.values()) + signs_and_symptoms_missing
    missing_percentage = (signs_and_symptoms_missing * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "signs_and_symptoms": symptoms_data,
        "signs_and_symptoms_missing": signs_and_symptoms_missing,
        "missing_percentage": f"{missing_percentage:.2f}".replace(",", ".")
    }