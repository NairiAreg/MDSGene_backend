import pandas as pd
import numpy as np
import os
import json
from utils import get_cached_dataframe, apply_filter, NumpyEncoder, safe_get

def get_unique_studies(disease_abbrev, gene, filter_criteria=None, aao=None, country=None, directory='excel'):
    results = []
    disease_abbrev = disease_abbrev.upper()

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

                for pmid in filtered_df['pmid'].unique():
                    try:
                        study_df = filtered_df[filtered_df['pmid'] == pmid]
                        number_of_cases = len(study_df)

                        study_design = safe_get(study_df, 'study_design', 0, 'Unknown')
                        ethnicity = safe_get(study_df, 'ethnicity', 0, 'Unknown')

                        proportion_of_male_patients = (
                            len(study_df[study_df['sex'] == 'male']) / number_of_cases
                            if number_of_cases > 0 else 0
                        )

                        mean_age_at_onset = study_df['aao'].mean()
                        mean_age_at_onset = (
                            float(mean_age_at_onset) if not pd.isna(mean_age_at_onset) else None
                        )

                        std_dev_age_at_onset = study_df['aao'].std()
                        std_dev_age_at_onset = (
                            float(std_dev_age_at_onset) if not pd.isna(std_dev_age_at_onset) else None
                        )

                        mutations = {
                            'mut1_p': safe_get(study_df, 'mut1_p', 0, 'Unknown'),
                            'mut2_p': safe_get(study_df, 'mut2_p', 0, 'Unknown'),
                            'mut3_p': safe_get(study_df, 'mut3_p', 0, 'Unknown'),
                            'mut1_genotype': safe_get(study_df, 'mut1_genotype', 0, 'Unknown'),
                            'mut2_genotype': safe_get(study_df, 'mut2_genotype', 0, 'Unknown'),
                            'mut3_genotype': safe_get(study_df, 'mut3_genotype', 0, 'Unknown')
                        }

                        result = {
                            'pmid': int(pmid) if isinstance(pmid, (np.integer, np.floating)) else pmid,
                            'study_design': study_design,
                            'number_of_cases': int(number_of_cases),
                            'ethnicity': ethnicity,
                            'proportion_of_male_patients': float(proportion_of_male_patients),
                            'mean_age_at_onset': mean_age_at_onset,
                            'std_dev_age_at_onset': std_dev_age_at_onset,
                            'mutations': mutations
                        }

                        result = json.loads(json.dumps(result, cls=NumpyEncoder))
                        results.append(result)
                    except Exception as e:
                        print(f"Error processing PMID {pmid} in file {filename}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results

def get_study_design_for_each_study(pmids, filter_criteria=None, aao=None, country=None, directory='excel'):
    study_design_list = []

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = get_cached_dataframe(file_path)
            df = df[df['ensemble_decision'] == 'IN']

            if filter_criteria is not None:
                df = apply_filter(df, filter_criteria, aao, country)

            pmid_list = list(map(int, pmids.split(',')))
            filtered_df = df[df['pmid'].isin(pmid_list)]
            study_design_list.extend(filtered_df['study_design'])

    return study_design_list

def get_number_of_cases_for_each_study(pmids, filter_criteria=None, aao=None, country=None, directory='excel'):
    number_of_cases_list = []

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = get_cached_dataframe(file_path)
            df = df[df['ensemble_decision'] == 'IN']

            if filter_criteria is not None:
                df = apply_filter(df, filter_criteria, aao, country)

            pmid_list = list(map(int, pmids.split(',')))
            filtered_df = df[df['pmid'].isin(pmid_list)]
            filtered_df = filtered_df.groupby('pmid').size().reset_index(name='number_of_cases')
            number_of_cases_map = dict(zip(filtered_df['pmid'], filtered_df['number_of_cases']))

    return number_of_cases_map