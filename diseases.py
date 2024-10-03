import os
import pandas as pd

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


def get_unique_disease_abbrev(directory='excel'):
    disease_abbrev_set = set()

    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)

            df = get_cached_dataframe(file_path)

            filtered_df = df[df['ensemble_decision'] == 'IN']

            # Convert disease_abbrev to uppercase before adding to the set
            disease_abbrev_set.update(filtered_df['disease_abbrev'].str.upper())

    return list(disease_abbrev_set)


def get_disease_and_genes(directory='excel'):
    disease_genes_list = []

    # Iterate through all files in the specified directory
    for filename in os.listdir(directory):
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            file_path = os.path.join(directory, filename)

            # Read the Excel file using the cache function
            df = get_cached_dataframe(file_path)

            # Filter the rows where 'ensemble_decision' is 'IN'
            filtered_df = df[df['ensemble_decision'] == 'IN']

            # Iterate through each row in the filtered DataFrame
            for _, row in filtered_df.iterrows():
                genes = []

                # Check and include gene1
                if pd.notna(row['gene1']) and row['gene1'] != '-99' and row['gene1'] != -99:
                    genes.append(row['gene1'])

                # Check and include gene2
                if pd.notna(row['gene2']) and row['gene2'] != '-99' and row['gene2'] != -99:
                    genes.append(row['gene2'])

                # Check and include gene3
                if pd.notna(row['gene3']) and row['gene3'] != '-99' and row['gene3'] != -99:
                    genes.append(row['gene3'])

                # Append the dictionary with non-blank and non '-99' gene values
                disease_genes_list.append({
                    'disease_abbrev': row['disease_abbrev'],
                    'genes': genes
                })

    return disease_genes_list
