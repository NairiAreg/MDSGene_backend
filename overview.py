import pandas as pd
import numpy as np
import os
import json

_dataframe_cache = {}

def get_cached_dataframe(file_path):
    global _dataframe_cache

    file_mod_time = os.path.getmtime(file_path)

    if file_path in _dataframe_cache and _dataframe_cache[file_path]['mod_time'] == file_mod_time:
        return _dataframe_cache[file_path]['dataframe']

    # Determine the file extension
    _, file_extension = os.path.splitext(file_path)
    
    # Choose the appropriate engine based on the file extension
    if file_extension.lower() == '.xlsx':
        engine = 'openpyxl'
    elif file_extension.lower() == '.xls':
        engine = 'xlrd'
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    # Read the Excel file with the specified engine
    df = pd.read_excel(file_path, engine=engine)

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

_dataframe_cache = {}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def safe_get(df, column, index, default=None):
    try:
        value = df[column].iloc[index]
        if pd.isna(value):
            return default
        if isinstance(value, (np.integer, np.floating)):
            return value.item()
        return value
    except:
        return default

def get_unique_studies(disease_abbrev, gene, filter_criteria=None, aao=None, country=None, directory='excel'):
    results = []

    for filename in os.listdir(directory):
        if filename.startswith('.~') or filename.startswith('~$'):
            continue  # Skip temporary Excel files
        
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df['ensemble_decision'] == 'IN']
                
                # Only apply the filter if filter_criteria is provided
                if filter_criteria is not None:
                    df = apply_filter(df, filter_criteria, aao, country)
                
                # Use pd.concat instead of append
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

                        # Convert numpy types to Python types
                        result = json.loads(json.dumps(result, cls=NumpyEncoder))
                        results.append(result)
                    except Exception as e:
                        print(f"Error processing PMID {pmid} in file {filename}: {str(e)}")
                        continue

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    return results

# Update other functions to handle optional parameters as well
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