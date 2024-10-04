import pandas as pd
import numpy as np
import os
import json
import logging
from utils import get_cached_dataframe, apply_filter, safe_get, NumpyEncoder

logger = logging.getLogger(__name__)


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

                # Use pd.concat instead of append
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

                for pmid in filtered_df["pmid"].unique():
                    try:
                        study_df = filtered_df[filtered_df["pmid"] == pmid]
                        number_of_cases = len(study_df)

                        study_design = safe_get(study_df, "study_design", 0, "Unknown")
                        ethnicity = safe_get(study_df, "ethnicity", 0, "Unknown")

                        proportion_of_male_patients = (
                            len(study_df[study_df["sex"] == "male"]) / number_of_cases
                            if number_of_cases > 0
                            else 0
                        )

                        mean_age_at_onset = study_df["aao"].mean()
                        mean_age_at_onset = (
                            float(mean_age_at_onset)
                            if not pd.isna(mean_age_at_onset)
                            else None
                        )

                        std_dev_age_at_onset = study_df["aao"].std()
                        std_dev_age_at_onset = (
                            float(std_dev_age_at_onset)
                            if not pd.isna(std_dev_age_at_onset)
                            else None
                        )

                        mutations = {
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
                            "pmid": (
                                int(pmid)
                                if isinstance(pmid, (np.integer, np.floating))
                                else pmid
                            ),
                            "study_design": study_design,
                            "number_of_cases": int(number_of_cases),
                            "ethnicity": ethnicity,
                            "proportion_of_male_patients": float(
                                proportion_of_male_patients
                            ),
                            "mean_age_at_onset": mean_age_at_onset,
                            "std_dev_age_at_onset": std_dev_age_at_onset,
                            "mutations": mutations,
                        }

                        result = json.loads(json.dumps(result, cls=NumpyEncoder))

                        results.append(result)
                    except Exception as e:
                        logger.error(
                            f"Error processing PMID {pmid} in file {filename}: {str(e)}"
                        )
                        continue

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return results

