# Send Author, year also, it shold be shown instead of pmid
# Send Mean AAO
# Ethnicities should be
# Add hint tooltips
# If no sex n.a should return not 0
# Write hom, comp. het etc...

import pandas as pd
import numpy as np
import os
import json
import logging
from utils import get_cached_dataframe, apply_filter, safe_get, NumpyEncoder

logger = logging.getLogger(__name__)


def to_python_type(value):
    if isinstance(value, (np.int64, np.int32)):
        return int(value)
    elif isinstance(value, (np.float64, np.float32)):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, (np.ndarray, list)):
        return [to_python_type(v) for v in value]
    elif isinstance(value, dict):
        return {k: to_python_type(v) for k, v in value.items()}
    return value


def get_mutations(df):
    mutations = []
    for _, row in df.iterrows():
        patient_mutations = []
        for i in range(1, 4):
            mut_p = row.get(f"mut{i}_p", -99)
            mut_g = row.get(f"mut{i}_g", -99)
            mut_c = row.get(f"mut{i}_c", -99)
            genotype = row.get(f"mut{i}_genotype", -99)

            if mut_p != -99 and mut_p is not None:
                mutation_name = mut_p
            elif mut_g != -99 and mut_g is not None:
                mutation_name = mut_g
            elif mut_c != -99 and mut_c is not None:
                mutation_name = mut_c
            else:
                continue  # Skip if no valid mutation found

            patient_mutations.append((mutation_name, genotype))

        # Process mutations for this patient
        if len(patient_mutations) == 0:
            mutations.append({"type": "single", "name": "n.a.", "genotype": "n.a."})
        elif len(patient_mutations) == 2 and all(
            m[1] == "het" for m in patient_mutations
        ):
            # Compound heterozygous
            mutations.append(
                {
                    "type": "compound_het",
                    "mutations": [
                        {"name": patient_mutations[0][0], "genotype": "het"},
                        {"name": patient_mutations[1][0], "genotype": "het"},
                    ],
                }
            )
        else:
            # Single mutations or non-compound het
            for mutation, genotype in patient_mutations:
                mutations.append(
                    {
                        "type": "single",
                        "name": mutation,
                        "genotype": genotype if genotype in ["hom", "het"] else "n.a.",
                    }
                )

    # Remove duplicates while preserving order
    unique_mutations = []
    seen = set()
    for m in mutations:
        m_key = str(m)  # Convert the dict to a string for hashing
        if m_key not in seen:
            unique_mutations.append(m)
            seen.add(m_key)

    return unique_mutations


def get_unique_studies(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    results = []
    logger.info(f"🔍 Starting search for {disease_abbrev}-{gene}")

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            logger.info(f"📂 Processing file: {filename}")
            try:
                df = get_cached_dataframe(file_path)

                # Apply ensemble_decision filter first
                df = df[df["ensemble_decision"] == "IN"]
                logger.info(
                    f"✅ Loaded dataframe from {filename}, shape after ensemble_decision filter: {df.shape}"
                )

                # Apply disease and gene filter
                df = df[
                    (df["disease_abbrev"] == disease_abbrev)
                    & (
                        (df["gene1"] == gene)
                        | (df["gene2"] == gene)
                        | (df["gene3"] == gene)
                    )
                ]
                logger.info(
                    f"🧬 Filtered for {disease_abbrev}-{gene}, shape: {df.shape}"
                )

                if (
                    filter_criteria is not None
                    or aao is not None
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, country, mutation)
                    logger.info(f"🔎 Applied additional filters, new shape: {df.shape}")

                logger.debug(f"🔬 Columns in filtered df: {df.columns}")

                for pmid in df["pmid"].unique():
                    try:
                        study_df = df[df["pmid"] == pmid]
                        logger.info(
                            f"📊 Processing PMID: {pmid}, rows: {len(study_df)}"
                        )

                        number_of_cases = len(study_df)
                        study_design = safe_get(study_df, "study_design", 0, "Unknown")
                        ethnicity = safe_get(study_df, "ethnicity", 0, -99)

                        if "author, year" in study_df.columns:
                            author_year = study_df["author, year"].iloc[0]
                            logger.info(f"📝 Author, year: {author_year}")
                        else:
                            author_year = "Unknown"
                            logger.warning(
                                f"⚠️ 'author, year' column not found for PMID {pmid}"
                            )

                        if author_year == "Unknown":
                            logger.warning(f"⚠️ Author, year is Unknown for PMID {pmid}")
                            logger.debug(f"🔬 Available columns: {study_df.columns}")
                            logger.debug(
                                f"🔬 First row of study_df: {study_df.iloc[0].to_dict()}"
                            )

                        sex_data = study_df["sex"].value_counts()
                        total_with_sex = sex_data.sum()
                        proportion_of_male_patients = (
                            -99
                            if (study_df["sex"] == -99).all()
                            else (
                                sex_data.get("male", 0) / total_with_sex
                                if total_with_sex > 0
                                else -99
                            )
                        )

                        aao_values = study_df["aao"].replace(-99, np.nan).dropna()
                        mean_age_at_onset = (
                            round(aao_values.mean()) if not aao_values.empty else -99
                        )
                        std_dev_age_at_onset = (
                            round(aao_values.std())
                            if not aao_values.empty and len(aao_values) > 1
                            else None
                        )

                        mutations = get_mutations(study_df)
                        full_mutations = {
                            "mut1_p": safe_get(study_df, "mut1_p", 0, "Unknown"),
                            "mut2_p": safe_get(study_df, "mut2_p", 0, "Unknown"),
                            "mut3_p": safe_get(study_df, "mut3_p", 0, "Unknown"),
                            "mut1_g": safe_get(study_df, "mut1_g", 0, "Unknown"),
                            "mut2_g": safe_get(study_df, "mut2_g", 0, "Unknown"),
                            "mut3_g": safe_get(study_df, "mut3_g", 0, "Unknown"),
                            "mut1_c": safe_get(study_df, "mut1_c", 0, "Unknown"),
                            "mut2_c": safe_get(study_df, "mut2_c", 0, "Unknown"),
                            "mut3_c": safe_get(study_df, "mut3_c", 0, "Unknown"),
                            "mut1_genotype": safe_get(
                                study_df, "mut1_genotype", 0, "Unknown"
                            ),
                            "mut2_genotype": safe_get(
                                study_df, "mut2_genotype", 0, "Unknown"
                            ),
                            "mut3_genotype": safe_get(
                                study_df, "mut3_genotype", 0, "Unknown"
                            ),
                        }

                        result = {
                            "pmid": to_python_type(pmid),
                            "author_year": author_year,  # Changed to snake_case
                            "study_design": study_design,
                            "number_of_cases": int(number_of_cases),
                            "ethnicity": to_python_type(ethnicity),
                            "proportion_of_male_patients": to_python_type(
                                proportion_of_male_patients
                            ),
                            "full_mutations": full_mutations,
                            "mean_age_at_onset": to_python_type(mean_age_at_onset),
                            "std_dev_age_at_onset": to_python_type(
                                std_dev_age_at_onset
                            ),
                            "mutations": mutations,  # Now this is a list of structured mutation objects
                        }

                        results.append(result)
                        logger.info(f"✅ Processed PMID: {pmid}")
                    except Exception as e:
                        logger.error(
                            f"❌ Error processing PMID {pmid} in file {filename}: {str(e)}"
                        )
                        logger.exception("Detailed error:")
                        continue

            except Exception as e:
                logger.error(f"❌ Error reading file {filename}: {str(e)}")
                logger.exception("Detailed error:")
                continue

    logger.info(f"🏁 Finished processing. Total results: {len(results)}")
    return results
