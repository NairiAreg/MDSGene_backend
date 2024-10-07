import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)

def _fetch_country_pie_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    country_counts = {}

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
                    & (filtered_df["country"].notnull())
                ]

                country_counts.update(filtered_df["country"].value_counts().to_dict())

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return country_counts

def _fetch_country_pie_missing(
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
                    & (filtered_df["country"].isnull())
                ]

                missing_count += filtered_df["patient_id"].nunique()

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return missing_count

def generate_country_pie_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    country_counts = _fetch_country_pie_chart(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    country_pie_missing = _fetch_country_pie_missing(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    total_eligible = sum(country_counts.values()) + country_pie_missing
    country_pie_missing_percentage = (country_pie_missing * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "country_pie_chart": country_counts,
        "country_pie_missing": country_pie_missing,
        "country_pie_missing_percentage": f"{country_pie_missing_percentage:.2f}".replace(",", ".")
    }