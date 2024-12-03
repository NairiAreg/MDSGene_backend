import numpy as np
import os
import logging
import re

import mutation_details
from utils import (
    get_cached_dataframe,
    apply_filter,
    safe_get,
    extract_year
)

from typing import List, Dict, Any

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


# Изменена функция get_mutations - добавлен параметр gene
def get_mutations(df, gene):  # <<<< ИЗМЕНЕНИЕ 1: добавлен параметр gene
    mutations = []

    for _, row in df.iterrows():
        # Инициализируем списки для каждого пациента
        patient_mutations = []
        het_mutations = []  # Важно: объявляем список здесь!

        for i in range(1, 4):
            # ИЗМЕНЕНИЕ 2: добавлена проверка гена мутации
            mutation_gene = row.get(f'gene{i}')
            if mutation_gene != gene:
                continue  # Пропускаем мутации других генов

            mut_p = row.get(f"mut{i}_p", -99)
            mut_c = row.get(f"mut{i}_c", -99)
            mut_g = row.get(f"mut{i}_g", -99)
            genotype = row.get(f"mut{i}_genotype", -99)
            pathogenicity = row.get(f"pathogenicity{i}", -99)

            if mut_p != -99 and mut_p is not None:
                mutation_name = mut_p
            elif mut_c != -99 and mut_c is not None:
                mutation_name = mut_c
            elif mut_g != -99 and mut_g is not None:
                mutation_name = mut_g
            else:
                continue  # Skip if no valid mutation found

            # Если это het мутация, добавляем в специальный список
            if genotype == "het":
                het_mutations.append({
                    "name": mutation_name,
                    "genotype": genotype,
                    "pathogenicity": pathogenicity,
                    "details": mutation_details.get_data_for_mutation_from_row(mutation_name, row)
                })
            else:
                # Не-het мутации добавляем как обычно
                patient_mutations.append({
                    "type": "single",
                    "name": mutation_name,
                    "genotype": genotype if genotype in ["hom", "het","comp_het"] else "n.a.",
                    "pathogenicity": pathogenicity if pathogenicity != -99 else "n.a.",
                    "details": mutation_details.get_data_for_mutation_from_row(mutation_name, row)
                })

        # Проверяем het мутации для compound heterozygous
        if len(het_mutations) > 1:
            # Создаем compound heterozygous запись
            patient_mutations.append({
                    "type": "compound_het",
                    "mutations": [
                        {
                        "name": mut["name"],
                        "genotype": "comp_het",
                        "pathogenicity": mut["pathogenicity"],
                        "details": mut["details"]
                    } for mut in het_mutations
                ]
            })
        elif len(het_mutations) == 1:
            # Если только одна het мутация, добавляем как обычную
            patient_mutations.append({
                        "type": "single",
                "name": het_mutations[0]["name"],
                "genotype": "het",
                "pathogenicity": het_mutations[0]["pathogenicity"],
                "details": het_mutations[0]["details"]
            })

        # Добавляем все мутации пациента в общий список
        mutations.extend(patient_mutations)

    return mutations


def mutation_key(mutation: Dict[str, Any]) -> tuple:
    if mutation["type"] == "compound_het":
        return (
            mutation["type"],
            tuple(
                sorted(
                    (
                        m.get("name", "Unknown"),
                        m.get("genotype", "Unknown"),
                        m.get("pathogenicity", "Unknown"),
                    )
                    for m in mutation["mutations"]
                )
            ),
        )
    else:
        return (
            mutation["type"],
            mutation.get("name", "Unknown"),
            mutation.get("genotype", "Unknown"),
            mutation.get("pathogenicity", "Unknown"),
        )


def get_unique_mutations(mutations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique_mutations = []
    seen = set()
    for mutation in mutations:
        try:
            key = mutation_key(mutation)
            if key not in seen:
                seen.add(key)
                unique_mutations.append(mutation)
        except KeyError as e:
            logger.warning(
                f"Skipping mutation due to missing key: {e}. Mutation data: {mutation}"
            )
    return unique_mutations


def find_author_year_column(columns):
    """Find the column that contains both 'author' and 'year' in its name."""
    pattern = re.compile(r".*author.*year.*|.*year.*author.*", re.IGNORECASE)
    matching_columns = [col for col in columns if pattern.match(str(col))]
    return matching_columns[0] if matching_columns else None


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

    print(
        f"Function parameters: disease_abbrev={disease_abbrev}, gene={gene}, filter_criteria={filter_criteria}, aao={aao}, country={country}, mutation={mutation}"
    )

    # Split disease_abbrev by underscore and convert each part to lowercase for case-insensitive comparison
    disease_parts = [part.lower() for part in disease_abbrev.split("_")]

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                print(f"\nProcessing file: {filename}")
                print(f"Initial DataFrame shape: {df.shape}")

                df = df[df["mdsgene_decision"] == "IN"]
                df = df[
                    df["disease_abbrev"]
                    .str.lower()
                    .apply(lambda x: all(part in x for part in disease_parts))
                    & (
                        (df["gene1"] == gene)
                        | (df["gene2"] == gene)
                        | (df["gene3"] == gene)
                    )
                ]

                print(f"DataFrame shape after initial filtering: {df.shape}")
                df = apply_filter(df, filter_criteria, aao, country, mutation)
                print(f"DataFrame shape after apply_filter: {df.shape}")

                # Find the author/year column
                author_year_col = find_author_year_column(df.columns)

                for pmid in df["pmid"].unique():
                    try:
                        study_df = df[df["pmid"] == pmid]
                        number_of_cases = len(study_df)
                        study_design = safe_get(study_df, "study_design", 0, "Unknown")
                        ethnicity = safe_get(study_df, "ethnicity", 0, -99)

                        # Use the detected column name or fall back to "Unknown"
                        author_year = (
                            study_df[author_year_col].iloc[0]
                            if author_year_col is not None
                            else "Unknown"
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

                        # ИЗМЕНЕНИЕ 3: передаем параметр gene в функцию get_mutations
                        mutations = get_mutations(study_df, gene)  # <<<< Добавлен параметр gene
                        unique_mutations = get_unique_mutations(mutations)

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
                            "author_year": author_year,
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
                            "mutations": unique_mutations,
                        }

                        results.append(result)
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

    results.sort(key=lambda x: extract_year(x["author_year"]), reverse=True)
    print(f"Total number of results: {len(results)}")
    return results
    # if results:
    #     cleaned_results = clean_study_mutations(results)
    #     return cleaned_results
