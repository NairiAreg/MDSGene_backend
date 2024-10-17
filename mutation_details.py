import pandas as pd
import numpy as np
import os
import json

import const
from utils import get_cached_dataframe, safe_get
from const import (
    protein_level_identifier_map,
    cdna_level_identifier_map,
    phosphorylation_activity_map,
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
                in [str(x) for x in const.chromosomes.values()] + ["x", "y", "m", "mt"]
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


def get_data_for_mutation_from_row(mutation_name, row):
    results = []
    for i in range(1, 4):
        protein_identifier = get_protein_identifier(row, i)
        cdna_identifier = get_cdna_identifier(row, i)
        gdna_identifier = get_gdna_identifier(row, i)
        if (
            mutation_name == protein_identifier
            or mutation_name == cdna_identifier
            or mutation_name == gdna_identifier
        ):
            result = {
                "proteinIdentifier": protein_level_identifier_map.get(
                    protein_identifier
                )
                or None,
                "proteinLevelIdentifier": (
                    protein_identifier
                    if protein_identifier not in [-99, "n.a.", "-99"]
                    else None
                ),
                "cdnaIdentifier": cdna_level_identifier_map.get(cdna_identifier)
                or None,
                "cdnaLevelIdentifier": (
                    cdna_identifier
                    if cdna_identifier not in [-99, "n.a.", "-99"]
                    else None
                ),
                "gdnaLevelIdentifier": (
                    gdna_identifier
                    if gdna_identifier not in [-99, "n.a.", "-99"]
                    else None
                ),
                "archiveIdentifierOtherDesignation": get_alias(row, i) or None,
                "referenceAlternativeAllele": (
                    get_allele(row, i) if get_allele(row, i) != "n.a." else None
                ),
                "genomicLocation": (
                    get_location(row, i) if get_location(row, i) != "n.a." else None
                ),
                "hg": get_hg_version(row) if get_hg_version(row) != "n.a." else None,
                "exac": (
                    get_link_to_exac(row, i)
                    if "not available on ExAC" not in get_link_to_exac(row, i)
                    else None
                ),
                "geneName": (
                    row.get(f"gene{i}")
                    if row.get(f"gene{i}") not in [-99, "n.a.", "-99"]
                    else None
                ),
                "geneLink": (
                    get_link_to_entrez_gene(row, i)
                    if get_link_to_entrez_gene(row, i) != "n.a."
                    else None
                ),
                "consequence": (
                    get_impact_humanize_downcase(row, i)
                    if get_impact_humanize_downcase(row, i) != "n.a."
                    else None
                ),
                "pathogenicityScoring": (
                    get_pathogenicity(row, i)
                    if get_pathogenicity(row, i) != "n.a."
                    else None
                ),
                "caddScore": (
                    get_cadd_score(row, i) if get_cadd_score(row, i) != "n.a." else None
                ),
                "phosphorylationActivity": phosphorylation_activity_map.get(
                    mutation_name
                )
                or None,
                "positiveFunctionalEvidence": get_functional_evidence(row),
            }
            results.append(result)
    return results


def get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, directory="excel"):
    results = []
    disease_abbrev = disease_abbrev.upper()
    pmid = int(pmid)  # Convert pmid to integer

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

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

                for _, row in filtered_df.iterrows():
                    for i in range(1, 4):
                        if (
                            row.get(f"mut{i}_p") == mut_p
                            or row.get(f"mut{i}_c") == mut_p
                            or row.get(f"mut{i}_g") == mut_p
                        ):

                            result = get_data_for_mutation_from_row(mut_p, row)
                            if result:
                                results.extend(result)

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results
