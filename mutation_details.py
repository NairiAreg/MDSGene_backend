import pandas as pd
import numpy as np
import os
import json
from utils import get_cached_dataframe, apply_filter, NumpyEncoder, safe_get
from const import protein_level_identifier_map, cdna_level_identifier_map

def get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, filter_criteria=None, aao=None, country=None, directory='excel'):
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

                if filter_criteria is not None:
                    df = apply_filter(df, filter_criteria, aao, country)

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