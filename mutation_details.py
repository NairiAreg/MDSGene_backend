import pandas as pd
import numpy as np
import os
import json

import const
from utils import get_cached_dataframe, safe_get
from const import protein_level_identifier_map, cdna_level_identifier_map, phosphorylation_activity_map


# Функция для получения данных о мутации на уровне белка
def get_protein_identifier(row, i):
    return row.get(f'mut{i}_p', None)

# Функция для получения данных о мутации на уровне cDNA
def get_cdna_identifier(row, i):
    return row.get(f'mut{i}_c', None)

# Функция для получения данных о мутации на уровне gDNA
def get_gdna_identifier(row, i):
    return row.get(f'mut{i}_g', None)

# Функция для получения архивного идентификатора или другого обозначения
def get_alias(row, i):
    return row.get(f'mut{i}_alias', None) if row.get(f'mut{i}_alias', None) != -99 else None

# Функция для получения аллелей (если оба аллеля указаны)
def get_allele(row, i):
    reference_allele = row.get(f'reference_allele{i}', None)
    observed_allele = row.get(f'observed_allele{i}', None)
    if reference_allele and observed_allele:
        return f"{reference_allele},{observed_allele}"
    return 'n.a.'

# Функция для получения геномного местоположения
def get_location(row, i):
    return row.get(f'physical_location{i}', 'n.a.')

# Функция для получения названия гена с ссылкой
def get_link_to_entrez_gene(row, i):
    gene = row.get(f'gene{i}', None)
    if gene:
        return f"https://www.ncbi.nlm.nih.gov/gene/?term={gene}"
    return 'n.a.'

# Функция для получения последствий мутации
def get_impact_humanize_downcase(row, i):
    return row.get(f'impact{i}', 'n.a.').lower()

# Функция для получения патогенности
def get_pathogenicity(row, i):
    return row.get(f'pathogenicity{i}', 'n.a.').lower()

# Функция для получения CADD score
def get_cadd_score(row, i):
    return row.get(f'cadd_{i}', 'n.a.')

# Функция для получения функциональных доказательств
def get_functional_evidence(row):
    evidence = [row.get(f'fun_evidence_pos_{i}', None) for i in range(1, 4)]
    #remove from evidence -99 substrings
    evidence = [e for e in evidence if e != -99]
    return [e for e in evidence if pd.notna(e)] or ['n.a.']

# Функция для получения данных о hg_version
def get_hg_version(row):
    return row.get('hg_version', 'n.a.')

# Функция для получения данных о доступности на ExAC
def get_exac(row, i):
    if row.get(f'exac_{i}', "").lower() == 'yes':
        return True
    return None

# Функция для получения данных о chromosome
def get_chromosome(row, i):
    physical_locaiion = row.get(f'physical_location{i}', None)
    if physical_locaiion:
        _temp = physical_locaiion.lower().split(":")
        if len(_temp) == 2 and (
        lambda: _temp[0] in [str(x) for x in const.chromosomes.values()] + ["x", "y", "m", "mt"])():
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
    physical_locaiion = row.get(f'physical_location{i}', None)
    if physical_locaiion:
        _temp = physical_locaiion.lower().split(":")
        if len(_temp) == 2 and _temp[1].isdigit():
            return _temp[1]
    return None

# Функция для получения ref
def get_ref(row, i):
    return row.get(f'reference_allele{i}', 'n.a.')

# Функция для получения alt
def get_alt(row, i):
    return row.get(f'observed_allele{i}', 'n.a.')

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

# def link_to_exac(row, i):
#     chr = get_chromosome(row, i)
#     spos = get_spos(row, i)
#     ref = get_ref(row, i)
#     alt = get_alt(row, i)
#     exac = row.get(f'exac{i}', 'no').lower() == 'yes'
#     hg = row.get(f'hg{i}', None)
#
#     if chr and spos:
#         text = f"{chr}:{spos}"
#         if exac and hg == 19:
#             var = f"{chr}-{spos}-{ref}-{alt}"
#             return f'<a href="{EXAC_BROWSER_URL}{var}?dataset=gnomad_r2_1" target="_blank">{text}</a>'
#         else:
#             return f"{text} (not available on ExAC)" if text != "null:null" else "not available"
#     return "not available"


def get_data_for_mutation_from_row(mutation_name, row):
    results = []
    for i in range(1, 4):
        protein_identifier = get_protein_identifier(row, i)
        cdna_identifier = get_cdna_identifier(row, i)
        gdna_identifier = get_gdna_identifier(row, i)
        if (mutation_name == protein_identifier or mutation_name == cdna_identifier or mutation_name == gdna_identifier):
            result = {
                'Protein identifier': protein_level_identifier_map.get(protein_identifier, None),
                'Protein level identifier': protein_identifier,
                'CDNA identifier': cdna_level_identifier_map.get(cdna_identifier, None),
                'cDNA level identifier': cdna_identifier,
                'GDNA level identifier': gdna_identifier,
                'Archive identifier/Other designation': get_alias(row, i),
                'Reference, alternative allele': get_allele(row, i),
                'Genomic location': get_location(row, i),
                'hg': get_hg_version(row),
                'exac': get_link_to_exac(row, i),
                'Gene name': row.get(f'gene{i}', None),
                'Gene link' : get_link_to_entrez_gene(row, i),
                'Consequence': get_impact_humanize_downcase(row, i),
                'Pathogenicity scoring': get_pathogenicity(row, i),
                'CADD score': get_cadd_score(row, i),
                'Phosphorylation activity': phosphorylation_activity_map.get(mutation_name, None),
                'Positive functional evidence': get_functional_evidence(row)
            }
            results.append(result)
    return results




def get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, directory='excel'):
    results = []
    disease_abbrev = disease_abbrev.upper()
    pmid = int(pmid)  # Convert pmid to integer

    for filename in os.listdir(directory):
        if filename.startswith('.~') or filename.startswith('~$'):
            continue

        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df['ensemble_decision'] == 'IN']

                df['disease_abbrev'] = df['disease_abbrev'].str.upper()

                filtered_df = pd.concat([
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene1'] == gene)],
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene2'] == gene)],
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene3'] == gene)]
                ])

                filtered_df = filtered_df[(filtered_df['pmid'] == pmid) &
                                          ((filtered_df['mut1_p'] == mut_p) |
                                           (filtered_df['mut2_p'] == mut_p) |
                                           (filtered_df['mut3_p'] == mut_p))]

                for _, row in filtered_df.iterrows():
                    mut_index = None
                    if row['mut1_p'] == mut_p:
                        mut_index = 1
                    elif row['mut2_p'] == mut_p:
                        mut_index = 2
                    elif row['mut3_p'] == mut_p:
                        mut_index = 3

                    if mut_index is not None:
                        result = {
                            'Protein level identifier': protein_level_identifier_map.get(mut_p, None),
                            'cDNA level identifier': cdna_level_identifier_map.get(
                                safe_get(row, f'mut{mut_index}_c', 0, None), None),
                            'Gene level identifier': safe_get(row, f'mut{mut_index}_g', 0, None),
                            'Archive identifier/Other designation': safe_get(row, f'mut{mut_index}_alias', 0, None),
                            'Reference, alternative allele': [safe_get(row, f'observed_allele{mut_index}', 0, None),
                                                              safe_get(row, f'reference_allele{mut_index}', 0, None)],
                            'hg': safe_get(row, 'hg_version', 0, None),
                            'Genomic location': safe_get(row, f'genomic_location{mut_index}', 0, None),
                            'Gene name': safe_get(row, f'gene{mut_index}', 0, None),
                            'Consequence': safe_get(row, 'impact', 0, None),
                            'Pathogenicity scoring': safe_get(row, f'pathogenicity{mut_index}', 0, None),
                            'CADD score': safe_get(row, f'CADD_{mut_index}', 0, None),
                            'Phosphorylation activity': safe_get(row, 'protein_related', 0, None),
                            'Positive functional evidence': safe_get(row, 'positive_evidence', 0, None),
                            'Number of all included cases': len(filtered_df[
                                ((filtered_df['mut1_p'] == mut_p) |
                                 (filtered_df['mut2_p'] == mut_p) |
                                 (filtered_df['mut3_p'] == mut_p)) &
                                (filtered_df['status_clinical'] != 'clinically unaffected') &
                                ((filtered_df['pathogenicity1'] != 'benign') |
                                 (filtered_df['pathogenicity2'] != 'benign') |
                                 (filtered_df['pathogenicity3'] != 'benign'))
                            ])
                        }
                        results.append(result)

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results