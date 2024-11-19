import pandas as pd
import numpy as np
import os
import json
import math
from utils import get_cached_dataframe, safe_get
from const import (
    protein_level_identifier_map,
    cdna_level_identifier_map,
    phosphorylation_activity_map,
    chromosomes,
)


# Функция для получения данных о мутации на уровне белка
def get_protein_identifier(row, i):
    return row.get(f"mut{i}_p", None)


# Функция для получения данных о мутации на уровне cDNA
def get_cdna_identifier(row, i):
    return row.get(f"mut{i}_c", None)


# Функция для получения данных о мутации на уровне gDNA
def get_gdna_identifier(row, i):
    return row.get(f"mut{i}_g", None)


# Функция для получения архивного идентификатора или другого обозначения
def get_alias(row, i):
    return (
        row.get(f"mut{i}_alias", None)
        if row.get(f"mut{i}_alias", None) != -99
        else None
    )


# Функция для получения аллелей (если оба аллеля указаны)
def get_allele(row, i):
    reference_allele = row.get(f"reference_allele{i}", None)
    observed_allele = row.get(f"observed_allele{i}", None)
    if reference_allele and observed_allele:
        return f"{reference_allele},{observed_allele}"
    return "n.a."


# Функция для получения геномного местоположения
def get_location(row, i):
    return row.get(f"physical_location{i}", "n.a.")


# Функция для получения названия гена с ссылкой
def get_link_to_entrez_gene(row, i):
    gene = row.get(f"gene{i}", None)
    if gene:
        return f"https://www.ncbi.nlm.nih.gov/gene/?term={gene}"
    return "n.a."


# Функция для получения последствий мутации
def get_impact_humanize_downcase(row, i):
    return row.get(f"impact{i}", "n.a.").lower()


# Функция для получения патогенности
def get_pathogenicity(row, i):
    return row.get(f"pathogenicity{i}", "n.a.").lower()


# Функция для получения CADD score
def get_cadd_score(row, i):
    return row.get(f"cadd_{i}", "n.a.")


# Функция для получения функциональных доказательств
def get_functional_evidence(row):
    evidence = [row.get(f"fun_evidence_pos_{i}", None) for i in range(1, 4)]
    evidence = [str(e) for e in evidence if e not in [-99, None, "n.a.", "-99", "NaN"]]
    return evidence if evidence else None


# Функция для получения данных о hg_version
def get_hg_version(row):
    return row.get("hg_version", "n.a.")


# Функция для получения данных о доступности на ExAC
def get_exac(row, i):
    if row.get(f"exac_{i}", "").lower() == "yes":
        return True
    return None


# Функция для получения данных о chromosome
def get_chromosome(row, i):
    physical_locaiion = row.get(f"physical_location{i}", None)
    if physical_locaiion:
        _temp = physical_locaiion.lower().split(":")
        if (
            len(_temp) == 2
            and (
                lambda: _temp[0]
                in [str(x) for x in chromosomes.values()] + ["x", "y", "m", "mt"]
            )()
        ):
            if _temp[0] == "x":
                return str(23)
            elif _temp[0] == "y":
                return str(24)
            elif _temp[0] in ["m", "mt"]:
                return str(25)
            else:
                return _temp[0]
    return "n.a."


# Функция для получения spos
def get_spos(row, i):
    physical_locaiion = row.get(f"physical_location{i}", None)
    if physical_locaiion:
        _temp = physical_locaiion.lower().split(":")
        if len(_temp) == 2 and _temp[1].isdigit():
            return _temp[1]
    return None


# Функция для получения ref
def get_ref(row, i):
    return row.get(f"reference_allele{i}", "n.a.")


# Функция для получения alt
def get_alt(row, i):
    return row.get(f"observed_allele{i}", "n.a.")


def get_link_to_exac(row, i):
    chrom = get_chromosome(row, i)
    spos = get_spos(row, i)
    ref = get_ref(row, i)
    alt = get_alt(row, i)
    exac = get_exac(row, i)
    hg = get_hg_version(row)
    EXAC_BROWSER_URL = "https://exac.broadinstitute.org/variant/"

    if chrom and spos:
        text = f"{chrom}:{spos}"
        if exac and hg == 19:
            var = f"{chrom}-{spos}-{ref}-{alt}"
            return f'<a href="{EXAC_BROWSER_URL}{var}?dataset=gnomad_r2_1" target="_blank">{text}</a>'
        else:
            return f"{text} (not available on ExAC)"

    return "not available"


def handle_value(value):
    """Safely handle any value for JSON serialization"""
    if pd.isna(value) or value in [-99, "-99"]:
        return "n.a."
    if isinstance(value, (float, np.float64, np.float32)):
        if math.isnan(value) or math.isinf(value):
            return "n.a."
        if value.is_integer():
            return int(value)
        return float(value)
    if isinstance(value, (int, np.int64, np.int32)):
        return int(value)
    if isinstance(value, np.ndarray):
        return [handle_value(v) for v in value]
    if value is None:
        return "n.a."
    return str(value)


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


def get_data_for_mutation_from_row(mutation_name, row):
    results = []
    for i in range(1, 4):
        protein_identifier = row.get(f"mut{i}_p", None)
        cdna_identifier = row.get(f"mut{i}_c", None)
        gdna_identifier = row.get(f"mut{i}_g", None)

        if (
            mutation_name == protein_identifier
            or mutation_name == cdna_identifier
            or mutation_name == gdna_identifier
        ):
            # Find all evidence columns
            evidence_columns = [col for col in row.keys() if "evidence" in col.lower()]

            # Extract evidence values
            functional_evidence = []
            for col in evidence_columns:
                evidence = row.get(col)
                if evidence not in [-99, None, "n.a.", "-99"] and not pd.isna(evidence):
                    functional_evidence.append(str(evidence))

            result = {
                "proteinIdentifier": handle_value(row.get(f"mut{i}_p", None)),
                "proteinLevelIdentifier": handle_value(protein_identifier),
                "cdnaIdentifier": handle_value(row.get(f"mut{i}_c", None)),
                "cdnaLevelIdentifier": handle_value(cdna_identifier),
                "gdnaLevelIdentifier": handle_value(gdna_identifier),
                "archiveIdentifierOtherDesignation": handle_value(
                    row.get(f"mut{i}_alias", None)
                ),
                "referenceAlternativeAllele": handle_value(
                    f"{row.get(f'reference_allele{i}', 'n.a.')},{row.get(f'observed_allele{i}', 'n.a.')}"
                ),
                "genomicLocation": handle_value(
                    row.get(f"physical_location{i}", "n.a.")
                ),
                "hg": handle_value(row.get("hg_version", "n.a.")),
                "geneName": handle_value(row.get(f"gene{i}", None)),
                "geneLink": f"https://www.ncbi.nlm.nih.gov/gene/?term={handle_value(row.get(f'gene{i}', 'n.a.'))}",
                "consequence": handle_value(row.get(f"impact{i}", "n.a.")).lower(),
                "pathogenicityScoring": handle_value(
                    row.get(f"pathogenicity{i}", "n.a.")
                ).lower(),
                "caddScore": handle_value(row.get(f"cadd_{i}", "n.a.")),
                "positiveFunctionalEvidence": functional_evidence,
            }
            results.append(result)

    return results


def get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, directory="excel"):
    results = []
    disease_abbrev = disease_abbrev.upper()
    pmid = int(pmid)

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)

                # Apply all filters using boolean indexing in one step
                mask = (
                    (df["ensemble_decision"] == "IN")
                    & (df["disease_abbrev"].str.upper() == disease_abbrev)
                    & (
                        (df["gene1"] == gene)
                        | (df["gene2"] == gene)
                        | (df["gene3"] == gene)
                    )
                    & (df["pmid"] == pmid)
                )

                filtered_df = df[mask]

                for _, row in filtered_df.iterrows():
                    mutation_data = get_data_for_mutation_from_row(mut_p, row)
                    if mutation_data:
                        results.extend(mutation_data)

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results
