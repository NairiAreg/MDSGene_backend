import pandas as pd
import os
import logging
import json
import re
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)


def load_symptom_categories(directory="excel"):
    """Load and flatten the symptom categories from JSON"""
    try:
        with open(os.path.join(directory, "symptom_categories.json"), "r") as f:
            categories = json.load(f)

        # Create a flattened mapping of all symptoms
        symptom_mapping = {}
        for category, symptoms in categories.items():
            if isinstance(symptoms, dict):
                for symptom_key, symptom_name in symptoms.items():
                    standardized_key = standardize_symptom(symptom_key)
                    if standardized_key:
                        symptom_mapping[standardized_key] = symptom_name

        return symptom_mapping
    except Exception as e:
        logger.error(f"Error loading symptom categories: {str(e)}")
        return {}


def standardize_symptom(symptom):
    """Standardize symptom names by removing common variations and special characters"""
    if not isinstance(symptom, str):
        return None

    # Convert to lowercase
    symptom = symptom.lower()

    # Remove common suffixes
    symptom = re.sub(r"_sympt$", "", symptom, flags=re.IGNORECASE)
    symptom = re.sub(r"_hp.*$", "", symptom, flags=re.IGNORECASE)

    # Remove special characters and extra spaces
    symptom = re.sub(r"[_\-/]", " ", symptom)
    symptom = re.sub(r"\s+", " ", symptom)
    symptom = symptom.strip()

    # Common replacements
    replacements = {
        "parkinsonian": "parkinson",
        "psychiatric": "psychotic",
        "psychological": "psychotic",
        "dysfunction": "disorder",
        "abnormality": "disorder",
    }

    for old, new in replacements.items():
        symptom = symptom.replace(old, new)

    return symptom


def get_standardized_symptom_name(symptom, symptom_mapping):
    """Get standardized symptom name using the mapping"""
    standardized = standardize_symptom(symptom)
    if standardized in symptom_mapping:
        return symptom_mapping[standardized]
    return standardized.title()  # Return capitalized version if no mapping found


def _fetch_initial_symptoms_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    initial_symptoms = {}
    total_patients = 0
    patients_with_missing_data = 0

    # Load symptom categories mapping
    symptom_mapping = load_symptom_categories(directory)

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)

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
                    & (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                ]

                total_patients += len(filtered_df)

                # Count patients with ALL initial symptoms missing or -99
                missing_mask = (
                    (
                        filtered_df["initial_sympt1"].isna()
                        | (filtered_df["initial_sympt1"] == -99)
                    )
                    & (
                        filtered_df["initial_sympt2"].isna()
                        | (filtered_df["initial_sympt2"] == -99)
                    )
                    & (
                        filtered_df["initial_sympt3"].isna()
                        | (filtered_df["initial_sympt3"] == -99)
                    )
                )
                patients_with_missing_data += missing_mask.sum()

                # Process valid symptoms
                for column in ["initial_sympt1", "initial_sympt2", "initial_sympt3"]:
                    if column in filtered_df.columns:
                        # Only count symptoms that are not null and not -99
                        valid_symptoms = filtered_df[
                            (~filtered_df[column].isna()) & (filtered_df[column] != -99)
                        ][column]

                        symptom_counts = valid_symptoms.value_counts().to_dict()
                        for symptom, count in symptom_counts.items():
                            standardized_name = get_standardized_symptom_name(
                                symptom, symptom_mapping
                            )
                            initial_symptoms[standardized_name] = (
                                initial_symptoms.get(standardized_name, 0) + count
                            )

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    # Add debug logging
    logger.debug(f"Total patients before percentage calc: {total_patients}")
    logger.debug(
        f"Missing patients before percentage calc: {patients_with_missing_data}"
    )

    return initial_symptoms, total_patients, patients_with_missing_data


def generate_initial_signs_symptoms(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
    directory: str = "excel",
):
    initial_symptoms, total_patients, patients_with_missing_data = (
        _fetch_initial_symptoms_data(
            disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
        )
    )

    # Sort symptoms by count in descending order
    sorted_symptoms = sorted(initial_symptoms.items(), key=lambda x: x[1], reverse=True)

    # Extract data for the result
    histogram_data = [
        {"symptom": symptom, "count": count} for symptom, count in sorted_symptoms
    ]

    # Calculate missing percentage
    hist_missing_percentage = (
        (patients_with_missing_data * 100.0) / total_patients
        if total_patients > 0
        else 0.0
    )

    # Add debug logging
    logger.debug(f"Total patients: {total_patients}")
    logger.debug(f"Patients with missing data: {patients_with_missing_data}")
    logger.debug(f"Missing percentage: {hist_missing_percentage:.2f}%")

    return {
        "chart": {"type": "column"},
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": "Initial Signs and Symptoms Histogram"},
        "subtitle": {
            "text": f"Number of patients with missing data: {patients_with_missing_data} ({hist_missing_percentage:.2f}%)"
        },
        "xAxis": {
            "categories": [item["symptom"] for item in histogram_data],
            "title": {"text": "Symptoms"},
        },
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "series": [
            {
                "name": "Patients",
                "data": [item["count"] for item in histogram_data],
                "color": "#A52A2A",
            }
        ],
    }
