import pandas as pd
import os
import logging
import re
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def standardize_symptom(symptom):
    """Standardize symptom names by removing common variations and special characters"""
    if not isinstance(symptom, str):
        return None

    # Convert to lowercase
    symptom = symptom.lower()

    # Remove common prefixes and suffixes
    # Option 1 - Using re.IGNORECASE flag
    symptom = re.sub(r"_sympt$", "", symptom, flags=re.IGNORECASE)
    symptom = re.sub(r"_hp.*$", "", symptom, flags=re.IGNORECASE)

    # Option 2 - Using inline (?i) flag
    symptom = re.sub(r"(?i)_sympt$", "", symptom)
    symptom = re.sub(r"(?i)_hp.*$", "", symptom)

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


def extract_unified_symptoms(directory="../excel"):
    symptom_set = set()
    column_values = defaultdict(set)

    try:
        # Process each Excel file
        for filename in os.listdir(directory):
            if filename.endswith((".xlsx", ".xls")) and not filename.startswith(
                (".~", "~$")
            ):
                file_path = os.path.join(directory, filename)
                try:
                    logger.info(f"Processing file: {filename}")
                    df = pd.read_excel(file_path)

                    # Convert column names to lowercase
                    df.columns = df.columns.str.lower()

                    # Extract symptoms from column names
                    symptom_columns = [
                        col for col in df.columns if "_sympt" in col or "_hp" in col
                    ]
                    for col in symptom_columns:
                        standardized = standardize_symptom(col)
                        if standardized:
                            symptom_set.add(standardized)

                        # Extract unique values from the column
                        unique_values = df[col].dropna().unique()
                        valid_values = [
                            str(val).lower()
                            for val in unique_values
                            if val != -99 and pd.notna(val)
                        ]
                        column_values[standardized].update(valid_values)

                    # Process initial symptoms
                    for i in range(1, 4):
                        col = f"initial_sympt{i}"
                        if col in df.columns:
                            unique_symptoms = df[col].dropna().unique()
                            valid_symptoms = [
                                str(s).lower()
                                for s in unique_symptoms
                                if s != -99 and pd.notna(s)
                            ]
                            for symptom in valid_symptoms:
                                standardized = standardize_symptom(symptom)
                                if standardized:
                                    symptom_set.add(standardized)

                except Exception as e:
                    logger.error(f"Error processing file {filename}: {str(e)}")
                    continue

        # Convert to sorted list
        unified_symptoms = sorted(list(symptom_set))

        # Log the results
        logger.info(
            f"\nFound {len(unified_symptoms)} unique symptoms after standardization:"
        )
        for symptom in unified_symptoms:
            logger.info(f"- {symptom}")
            if symptom in column_values:
                logger.info(
                    f"  Values found: {', '.join(sorted(column_values[symptom]))}"
                )

        return unified_symptoms

    except Exception as e:
        logger.error(f"Error in main extraction process: {str(e)}")
        return []


if __name__ == "__main__":
    symptoms = extract_unified_symptoms()
    print(f"\nExtracted {len(symptoms)} unified symptoms.")
    print(symptoms)  # Will print the array of unified symptoms
