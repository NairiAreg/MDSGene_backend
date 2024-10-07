import pandas as pd
import os
import logging
from utils import get_cached_dataframe

logger = logging.getLogger(__name__)

def _fetch_symptoms_ordered_by_name(directory: str = "excel"):
    symptoms = set()

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                for column in df.columns:
                    if column.endswith("_sympt") or "_hp:" in column:
                        symptoms.add(column)

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return sorted(symptoms)

def _count_initial_symptoms(
    disease_abbrev: str,
    gene: str,
    symptom_id: int,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    count = 0

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
                    & (filtered_df["symptom_id"] == symptom_id)
                    & (filtered_df["initial"] == True)
                ]

                count += filtered_df["patient_id"].nunique()

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return count

def _fetch_initial_symptoms_missing(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    missing_patients = []

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

                grouped = filtered_df.groupby("patient_id").agg({"initial": "sum"})
                missing_patients.extend(grouped[grouped["initial"] == 0].index.tolist())

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return len(missing_patients)

def generate_initial_signs_symptoms(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    symptoms = _fetch_symptoms_ordered_by_name(directory)
    initial_signs_symptoms = []

    for symptom in symptoms:
        count = _count_initial_symptoms(
            disease_abbrev,
            gene,
            symptom,
            filter_criteria,
            country,
            mutation,
            directory
        )

        if count > 0:
            symptom_name = symptom.split("_hp:")[0].split("_sympt")[0]
            initial_signs_symptoms.append([symptom_name, count])

    initial_signs_symptoms.sort(key=lambda x: x[1], reverse=True)

    initial_signs_symptoms_missing = _fetch_initial_symptoms_missing(
        disease_abbrev,
        gene,
        filter_criteria,
        country,
        mutation,
        directory
    )

    total_eligible = sum([count for _, count in initial_signs_symptoms]) + initial_signs_symptoms_missing
    initial_missing_percentage = (initial_signs_symptoms_missing * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "initial_signs_symptoms": initial_signs_symptoms,
        "initial_signs_symptoms_missing": initial_signs_symptoms_missing,
        "initial_missing_percentage": f"{initial_missing_percentage:.2f}".replace(",", ".")
    }