# study_details.py
import pandas as pd
import numpy as np
import os
import json
from utils import get_cached_dataframe, apply_filter

def get_patients_for_publication(disease_abbrev, gene, pmid, filter_criteria=None, aao=None, country=None, mutation = None, directory='excel'):
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

                if (
                    filter_criteria is not None
                    or aao is not None
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, country, mutation)

                filtered_df = pd.concat([
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene1'] == gene)],
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene2'] == gene)],
                    df[(df['disease_abbrev'] == disease_abbrev) & (df['gene3'] == gene)]
                ])

                filtered_df = filtered_df[filtered_df['pmid'] == pmid]

                for _, row in filtered_df.iterrows():
                    symptoms = {col: row[col] for col in filtered_df.columns if '_sympt' in col or '_hp' in col}
                    initial_symptoms = [row[col] for col in ['initial_sympt1', 'initial_sympt2', 'initial_sympt3'] if pd.notna(row[col])]
                    mutations = {
                        'mut1_p': row['mut1_p'],
                        'mut2_p': row['mut2_p'],
                        'mut3_p': row['mut3_p'],
                        'mut1_genotype': row['mut1_genotype'],
                        'mut2_genotype': row['mut2_genotype'],
                        'mut3_genotype': row['mut3_genotype']
                    }

                    result = {
                        'index_patient': row['index_pat'],
                        'sex': row['sex'],
                        'ethnicity': row['ethnicity'],
                        'country_of_origin': row['country'],
                        'aao': row['aao'],
                        'aae': row['aae'],
                        'family_history': row['famhx'],
                        'symptoms': symptoms,
                        'initial_symptoms': initial_symptoms,
                        'reported_mutations': mutations
                    }

                    results.append(result)

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results