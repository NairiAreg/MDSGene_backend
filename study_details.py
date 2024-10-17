import pandas as pd
import numpy as np
import os
import logging
from utils import get_cached_dataframe, apply_filter
import mutation_details  # Assuming this module exists for get_data_for_mutation_from_row

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_mutations_for_patient(row):
    patient_mutations = []
    for i in range(1, 4):
        mut_p = row.get(f"mut{i}_p", -99)
        mut_c = row.get(f"mut{i}_c", -99)
        genotype = row.get(f"mut{i}_genotype", -99)

        if mut_p not in [-99, None, "-99"]:
            mutation_name = mut_p
        elif mut_c not in [-99, None, "-99"]:
            mutation_name = mut_c
        else:
            continue  # Skip if no valid mutation found

        patient_mutations.append((mutation_name, genotype))

    if len(patient_mutations) == 0:
        return [{"type": "single", "name": "n.a.", "genotype": "n.a."}]
    elif len(patient_mutations) == 2 and all(m[1] == "het" for m in patient_mutations):
        # Compound heterozygous
        return [
            {
                "type": "compound_het",
                "mutations": [
                    {
                        "name": patient_mutations[0][0],
                        "genotype": "het",
                        "details": mutation_details.get_data_for_mutation_from_row(
                            patient_mutations[0][0], row
                        ),
                    },
                    {
                        "name": patient_mutations[1][0],
                        "genotype": "het",
                        "details": mutation_details.get_data_for_mutation_from_row(
                            patient_mutations[1][0], row
                        ),
                    },
                ],
            }
        ]
    else:
        # Single mutations or non-compound het
        return [
            {
                "type": "single",
                "name": mutation,
                "genotype": genotype if genotype in ["hom", "het"] else "n.a.",
                "details": mutation_details.get_data_for_mutation_from_row(
                    mutation, row
                ),
            }
            for mutation, genotype in patient_mutations
        ]


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
    pmid = int(pmid)  # Convert pmid to integer
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

            if "ensemble_decision" in df.columns:
                df = df[df["ensemble_decision"] == "IN"]
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

            logger.debug(
                f"Dataframe shape after initial filtering: {filtered_df.shape}"
            )

            if (
                filter_criteria is not None
                or aao is not None
                or country is not None
                or mutation is not None
            ):
                filtered_df = apply_filter(
                    filtered_df, filter_criteria, aao, country, mutation
                )
                logger.debug(
                    f"Dataframe shape after applying additional filters: {filtered_df.shape}"
                )

            for _, row in filtered_df.iterrows():
                symptoms = [
                    col.replace("_sympt", "").replace("_hp", "")
                    for col in filtered_df.columns
                    if ("_sympt" in col or "_hp" in col)
                    and row.get(col) in [1, True, "yes", "Yes"]
                ]

                initial_symptoms = [
                    row.get(col)
                    for col in ["initial_sympt1", "initial_sympt2", "initial_sympt3"]
                    if pd.notna(row.get(col)) and row.get(col) not in [-99, "-99"]
                ]

                mutations = get_mutations_for_patient(row)

                result = {
                    "index_patient": (
                        "Yes"
                        if row.get("index_pat") in [1, True, "yes", "Yes"]
                        else "No"
                    ),
                    "sex": (
                        row.get("sex")
                        if pd.notna(row.get("sex"))
                        and row.get("sex") not in [-99, "-99"]
                        else "n.a."
                    ),
                    "ethnicity": (
                        row.get("ethnicity")
                        if pd.notna(row.get("ethnicity"))
                        and row.get("ethnicity") not in [-99, "-99"]
                        else "n.a."
                    ),
                    "country_of_origin": (
                        row.get("country")
                        if pd.notna(row.get("country"))
                        and row.get("country") not in [-99, "-99"]
                        else "n.a."
                    ),
                    "aao": (
                        int(row.get("aao"))
                        if pd.notna(row.get("aao"))
                        and row.get("aao") not in [-99, "-99"]
                        else "n.a."
                    ),
                    "aae": (
                        int(row.get("aae"))
                        if pd.notna(row.get("aae"))
                        and row.get("aae") not in [-99, "-99"]
                        else "n.a."
                    ),
                    "family_history": (
                        "Yes" if row.get("famhx") in [1, True, "yes", "Yes"] else "No"
                    ),
                    "symptoms": symptoms,
                    "initial_symptoms": initial_symptoms,
                    "reported_mutations": mutations,
                }

                results.append(result)
                logger.debug(f"Added result: {result}")

        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            continue

    logger.debug(f"Total results found: {len(results)}")
    return results
