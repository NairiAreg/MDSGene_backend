import pandas as pd
import numpy as np
import os
import logging
import math
from utils import get_cached_dataframe, apply_filter
from mutation_details import handle_value, get_data_for_mutation_from_row

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def safe_handle_list(value_list):
    """Safely handle lists of values"""
    if value_list is None:
        return []
    if isinstance(value_list, (list, np.ndarray)):
        return [
            handle_value(v)
            for v in value_list
            if v not in [-99, "-99", None] and not pd.isna(v)
        ]
    return []


def get_mutations_for_patient(row):
    all_mutations = []

    # Внешний цикл по типам мутаций
    for mutation_type in ['p', 'c', 'g']:
        patient_mutations = []

        for i in range(1, 4):
            mutation_name = row.get(f"mut{i}_{mutation_type}", -99)
            genotype = row.get(f"mut{i}_genotype", -99)

            if mutation_name not in [-99, None, "-99"] and not pd.isna(mutation_name):
                patient_mutations.append((mutation_name, genotype))

        if len(patient_mutations) == 0:
            continue  # Пропускаем пустые мутации для данного типа
        elif len(patient_mutations) == 2 and all(m[1] == "het" for m in patient_mutations):
            all_mutations.append({
                "type": "compound_het",
                "mutations": [
                    {
                        "name": handle_value(patient_mutations[0][0]),
                        "genotype": "het",
                        "details": get_data_for_mutation_from_row(
                            patient_mutations[0][0], row
                        ),
                    },
                    {
                        "name": handle_value(patient_mutations[1][0]),
                        "genotype": "het",
                        "details": get_data_for_mutation_from_row(
                            patient_mutations[1][0], row
                        ),
                    },
                ],
            })
        else:
            all_mutations.extend([
                {
                    "type": "single",
                    "name": handle_value(mutation),
                    "genotype": genotype if genotype in ["hom", "het", "comp_het", "hemi"] else "n.a.",
                    "details": get_data_for_mutation_from_row(mutation, row),
                }
                for mutation, genotype in patient_mutations
            ])

    # Если нет мутаций ни одного типа, возвращаем n.a.
    if not all_mutations:
        return [{"type": "single", "name": "n.a.", "genotype": "n.a."}]

    return all_mutations


def get_patients_for_publication(
    disease_abbrev,
    gene,
    pmid,
    filter_criteria=None,
    aao=None,
    country=None,
    mutation=None,
    directory="excel",
):
    results = []
    disease_abbrev = disease_abbrev.upper()
    logger.debug(f"Searching for disease: {disease_abbrev}, gene: {gene}, pmid: {pmid}")

    for filename in os.listdir(directory):
        if (
            filename.startswith(".~")
            or filename.startswith("~$")
            or not (filename.endswith(".xlsx") or filename.endswith(".xls"))
        ):
            continue

        file_path = os.path.join(directory, filename)
        logger.debug(f"Processing file: {filename}")

        try:
            df = get_cached_dataframe(file_path)
            logger.debug(f"Dataframe shape after loading: {df.shape}")
            logger.debug(f"Available columns: {df.columns.tolist()}")

            if "mdsgene_decision" in df.columns:
                df = df[df["mdsgene_decision"] == "IN"]
                logger.debug(
                    f"Dataframe shape after ensemble decision filter: {df.shape}"
                )

            df["disease_abbrev"] = df["disease_abbrev"].str.upper()

            filtered_df = df[
                (df["disease_abbrev"] == disease_abbrev)
                & (
                    (df["gene1"] == gene)
                    | (df["gene2"] == gene)
                    | (df["gene3"] == gene)
                )
                & (df["pmid"] == pmid)
            ]

            logger.debug(f"Initial filtered dataframe for PMID {pmid}:")
            logger.debug(f"Number of rows: {len(filtered_df)}")
            if not filtered_df.empty:
                logger.debug("Sample of country values in filtered data:")
                logger.debug(filtered_df["country"].head())
                logger.debug("Unique country values in filtered data:")
                logger.debug(filtered_df["country"].unique())

            if any(x is not None for x in [filter_criteria, aao, country, mutation]):
                filtered_df = apply_filter(
                    filtered_df, filter_criteria, aao, country, mutation
                )
                logger.debug(
                    f"Dataframe shape after applying additional filters: {filtered_df.shape}"
                )

            for idx, row in filtered_df.iterrows():
                symptoms = [
                    handle_value(col.replace("_sympt", "").replace("_hp", ""))
                    for col in filtered_df.columns
                    if ("_sympt" in col or "_hp" in col)
                    and row.get(col) in [1, True, "yes", "Yes"]
                ]

                initial_symptoms = [
                    handle_value(row.get(col))
                    for col in ["initial_sympt1", "initial_sympt2", "initial_sympt3"]
                    if pd.notna(row.get(col)) and row.get(col) not in [-99, "-99"]
                ]

                mutations = get_mutations_for_patient(row)

                # Get country value with detailed logging
                country_value = row.get("country")
                logger.debug(f"Raw country value for row {idx}: {country_value}")
                logger.debug(f"Type of country value: {type(country_value)}")

                # Check for various invalid values
                is_invalid = (
                    country_value in [-99, "-99", None]
                    or pd.isna(country_value)
                    or (isinstance(country_value, str) and country_value.strip() == "")
                )
                logger.debug(f"Is country value invalid? {is_invalid}")

                country_str = handle_value(country_value) if not is_invalid else "n.a."
                logger.debug(f"Processed country value: {country_str}")

                result = {
                    "index_patient": (
                        "Yes"
                        if row.get("index_pat") in [1, True, "yes", "Yes"]
                        else "No"
                    ),
                    "sex": handle_value(row.get("sex")),
                    "ethnicity": handle_value(row.get("ethnicity")),
                    "country_of_origin": country_str,
                    "aao": handle_value(row.get("aao")),
                    "aae": handle_value(row.get("aae")),
                    "family_history": (
                        "Yes" if row.get("famhx") in [1, True, "yes", "Yes"] else "No"
                    ),
                    "symptoms": safe_handle_list(symptoms),
                    "initial_symptoms": safe_handle_list(initial_symptoms),
                    "reported_mutations": mutations,
                }

                results.append(result)
                logger.debug(
                    f"Added result with country: {result['country_of_origin']}"
                )

        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            logger.exception("Detailed error traceback:")
            continue

    logger.debug(f"Total results found: {len(results)}")
    # Log a summary of countries in results
    country_summary = [r["country_of_origin"] for r in results]
    logger.debug(f"Countries in final results: {country_summary}")

    return results
