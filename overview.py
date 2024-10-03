import pandas as pd
import os

_dataframe_cache = {}

def get_cached_dataframe(file_path):
    global _dataframe_cache

    file_mod_time = os.path.getmtime(file_path)

    if file_path in _dataframe_cache and _dataframe_cache[file_path]['mod_time'] == file_mod_time:
        return _dataframe_cache[file_path]['dataframe']

    df = pd.read_excel(file_path)

    _dataframe_cache[file_path] = {
        'dataframe': df,
        'mod_time': file_mod_time
    }

    return df

def apply_filter(df, filter_criteria, aao, country):
    if filter_criteria == 1:
        df = df[df['index_pat'] == 'yes']
    elif filter_criteria == 2 and aao is not None:
        df = df[df['aao'] < aao]
    elif filter_criteria == 3 and aao is not None:
        df = df[df['aao'] >= aao]
    elif filter_criteria == 4:
        df = df[df['sex'] == 'female']
    elif filter_criteria == 5:
        df = df[df['sex'] == 'male']
    elif filter_criteria == 6:
        df = df[(df['mut1_genotype'] == 'hom') | (df['mut2_genotype'] == 'hom') | (df['mut3_genotype'] == 'hom')]
    elif filter_criteria == 7:
        df = df[(df['mut1_genotype'] == 'het') | (df['mut2_genotype'] == 'het') | (df['mut3_genotype'] == 'het')]
    elif filter_criteria == 8:
        df = df[(df['mut1_genotype'] == 'comp_het') | (df['mut2_genotype'] == 'comp_het') | (df['mut3_genotype'] == 'comp_het')]
    elif filter_criteria == 9:
        df = df[(df['mut1_genotype'].isin(['hom', 'comp_het'])) | (df['mut2_genotype'].isin(['hom', 'comp_het'])) | (df['mut3_genotype'].isin(['hom', 'comp_het']))]

    if country:
        country_map = {
            'AUS': 'Austria',
            'FRA': 'France',
            'GER': 'Germany',
            'IND': 'India',
            'ITA': 'Italy',
            'PAK': 'Pakistan',
            'PRI': 'Puerto Rico',
            'UK': 'United Kingdom',
            'USA': 'United States'
        }
        if country in country_map:
            df = df[df['country'] == country_map[country]]

    return df

def get_unique_studies(disease_abbrev, gene, filter_criteria, aao, country, directory='excel'):
    results = []

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = get_cached_dataframe(file_path)
            df = df[df['ensemble_decision'] == 'IN']
            df = apply_filter(df, filter_criteria, aao, country)
            filtered_df = df[(df['disease_abbrev'] == disease_abbrev) & (df['gene1'] == gene)]
            filtered_df = filtered_df.append(df[(df['disease_abbrev'] == disease_abbrev) & (df['gene2'] == gene)])
            filtered_df = filtered_df.append(df[(df['disease_abbrev'] == disease_abbrev) & (df['gene3'] == gene)])

            for pmid in filtered_df['pmid'].unique():
                study_df = filtered_df[filtered_df['pmid'] == pmid]
                study_design = study_df['study_design'].iloc[0]
                number_of_cases = len(study_df)
                ethnicity = study_df['ethnicity'].iloc[0]
                proportion_of_male_patients = len(study_df[study_df['sex'] == 'male']) / number_of_cases
                mean_age_at_onset = study_df['aao'].mean()
                std_dev_age_at_onset = study_df['aao'].std()
                mutations = {
                    'mut1_p': study_df['mut1_genotype'].iloc[0],
                    'mut2_p': study_df['mut2_genotype'].iloc[0],
                    'mut3_p': study_df['mut3_genotype'].iloc[0]
                }

                results.append({
                    'pmid': pmid,
                    'study_design': study_design,
                    'number_of_cases': number_of_cases,
                    'ethnicity': ethnicity,
                    'proportion_of_male_patients': proportion_of_male_patients,
                    'mean_age_at_onset': mean_age_at_onset,
                    'std_dev_age_at_onset': std_dev_age_at_onset,
                    'mutations': mutations
                })

    return results

def get_study_design_for_each_study(pmids, filter_criteria, aao, country, directory='excel'):
    study_design_list = []

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = get_cached_dataframe(file_path)
            df = df[df['ensemble_decision'] == 'IN']
            df = apply_filter(df, filter_criteria, aao, country)
            pmid_list = list(map(int, pmids.split(',')))
            filtered_df = df[df['pmid'].isin(pmid_list)]
            study_design_list.extend(filtered_df['study_design'])

    return study_design_list

def get_number_of_cases_for_each_study(pmids, filter_criteria, aao, country, directory='excel'):
    number_of_cases_list = []

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            df = get_cached_dataframe(file_path)
            df = df[df['ensemble_decision'] == 'IN']
            df = apply_filter(df, filter_criteria, aao, country)
            pmid_list = list(map(int, pmids.split(',')))
            filtered_df = df[df['pmid'].isin(pmid_list)]
            filtered_df = filtered_df.groupby('pmid').size().reset_index(name='number_of_cases')
            number_of_cases_map = dict(zip(filtered_df['pmid'], filtered_df['number_of_cases']))

    return number_of_cases_map