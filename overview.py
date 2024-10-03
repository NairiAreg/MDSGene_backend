import pandas as pd
import os

# Dictionary to store cached data and their modification time
_dataframe_cache = {}

def get_cached_dataframe(file_path):
    global _dataframe_cache

    # Get the last modification time of the file
    file_mod_time = os.path.getmtime(file_path)

    # Check if the file is in the cache and if it is up to date
    if file_path in _dataframe_cache and _dataframe_cache[file_path]['mod_time'] == file_mod_time:
        return _dataframe_cache[file_path]['dataframe']

    # If the file is not cached or it has been modified, read it again
    df = pd.read_excel(file_path)

    # Cache the dataframe with its modification time
    _dataframe_cache[file_path] = {
        'dataframe': df,
        'mod_time': file_mod_time
    }

    return df

#на входе disease_abbrev и ген и на выходе список pmid
def get_unique_studies(disease_abbrev, gene, directory='excel'):
    pmid_list = []

    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)

            # Read the Excel file using the cache function
            df = get_cached_dataframe(file_path)

            # Filter the rows where 'ensemble_decision' is 'IN'
            df = df[df['ensemble_decision'] == 'IN']

            # Filter the rows where 'disease_abbrev' and 'gene' match the input values
            filtered_df = df[(df['disease_abbrev'] == disease_abbrev) & (df['gene1'] == gene)]

            # the same for gene2 and gene3
            filtered_df = filtered_df.append(df[(df['disease_abbrev'] == disease_abbrev) & (df['gene2'] == gene)])

            filtered_df = filtered_df.append(df[(df['disease_abbrev'] == disease_abbrev) & (df['gene3'] == gene)])

            # Add 'pmid' values to the list
            pmid_list.extend(filtered_df['pmid'])

    return pmid_list


def get_study_design_for_each_study(disease_abbrev, gene, pmids:str, directory='excel'):
    study_design_list = []

    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)

            # Read the Excel file using the cache function
            df = get_cached_dataframe(file_path)

            # Filter the rows where 'ensemble_decision' is 'IN'
            filtered_df = df[df['ensemble_decision'] == 'IN']

            # Convert the input string to a list of integers
            pmid_list = list(map(int, pmids.split(',')))

            # Filter the rows where 'pmid' is in the input list
            filtered_df = df[df['pmid'].isin(pmid_list)]

            # Add 'study_design' values to the list
            study_design_list.extend(filtered_df['study_design'])

    return study_design_list


# Add a new function to get the number of cases for each study in a list of PMIDs
def get_number_of_cases_for_each_study(pmids:str, directory='excel'):
    number_of_cases_list = []

    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)

            # Read the Excel file using the cache function
            df = get_cached_dataframe(file_path)

            # Filter the rows where 'ensemble_decision' is 'IN'
            filtered_df = df[df['ensemble_decision'] == 'IN']

            # Convert the input string to a list of integers
            pmid_list = list(map(int, pmids.split(',')))

            # Filter the rows where 'pmid' is in the input list
            filtered_df = df[df['pmid'].isin(pmid_list)]

            # number of cases should be related to the amount of the patients for each pmid each line is one patient
            filtered_df = filtered_df.groupby('pmid').size().reset_index(name='number_of_cases')

            # get map of pmid and number of cases
            number_of_cases_map = dict(zip(filtered_df['pmid'], filtered_df['number_of_cases']))

    return number_of_cases_map