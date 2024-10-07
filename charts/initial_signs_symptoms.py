import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)

def _fetch_initial_symptoms_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    initial_symptoms = {}
    total_patients = 0
    patients_with_missing_data = 0

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
                        df[(df["disease_abbrev"] == disease_abbrev) & (df["gene1"] == gene)],
                        df[(df["disease_abbrev"] == disease_abbrev) & (df["gene2"] == gene)],
                        df[(df["disease_abbrev"] == disease_abbrev) & (df["gene3"] == gene)],
                    ]
                )

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                ]

                total_patients += len(filtered_df)
                patients_with_missing_data += filtered_df[
                    ["initial_sympt1", "initial_sympt2", "initial_sympt3"]
                ].isnull().any(axis=1).sum()

                for column in ["initial_sympt1", "initial_sympt2", "initial_sympt3"]:
                    if column in filtered_df.columns:
                        symptom_counts = filtered_df[column].value_counts().to_dict()
                        for symptom, count in symptom_counts.items():
                            if symptom in initial_symptoms:
                                initial_symptoms[symptom] += count
                            else:
                                initial_symptoms[symptom] = count

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return initial_symptoms, total_patients, patients_with_missing_data

def generate_initial_signs_symptoms(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    initial_symptoms, total_patients, patients_with_missing_data = _fetch_initial_symptoms_data(
        disease_abbrev, gene, filter_criteria, country, mutation, directory
    )

    # Sort symptoms by count in descending order
    sorted_symptoms = sorted(initial_symptoms.items(), key=lambda x: x[1], reverse=True)

    # Extract data for the result
    histogram_data = [{"symptom": symptom, "count": count} for symptom, count in sorted_symptoms]

    total_eligible = total_patients  # Assuming total_eligible is equivalent to total_patients for now
    hist_missing_percentage = (patients_with_missing_data * 100.0) / total_eligible if total_eligible > 0 else 0.0

    return {
        "chart": {"type": "column"},
        "title": {"text": "Initial Signs and Symptoms Histogram"},
        "subtitle": {
            "text": f"Number of patients with missing data: {patients_with_missing_data} ({hist_missing_percentage}%)"
        },
        "xAxis": {"categories": [item["symptom"] for item in histogram_data], "title": {"text": "Symptoms"}},
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "series": [
            {"name": "Patients", "data": [item["count"] for item in histogram_data], "color": "#A52A2A"}
            # Dark red color
        ],
    }
