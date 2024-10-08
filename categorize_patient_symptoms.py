import json
import re

from utils import get_cached_dataframe


# Define function to categorize symptoms based on the properties file
def load_properties_file(file_path):
    with open(file_path, 'r') as file:
        properties = {}
        for line in file:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                symptoms = value.strip('[]').split(',')
                properties[key.strip()] = [symptom.strip() for symptom in symptoms]
    return properties


def categorize_symptoms(df, properties):
    # Extract columns that end with '_sympt' or '_hp:number'
    symptom_columns = [col for col in df.columns if re.search(r'_sympt$|_hp:\d+$', col)]

    categorized_symptoms = {category: [] for category in properties.keys()}
    uncategorized_symptoms = []

    for symptom in symptom_columns:
        added = False
        for category, symptoms_list in properties.items():
            if symptom in symptoms_list:
                categorized_symptoms[category].append(symptom)
                added = True
                break
        if not added:
            uncategorized_symptoms.append(symptom)

    return categorized_symptoms, uncategorized_symptoms


def mark_initial_symptoms(df, symptom_columns):
    initial_sympt_cols = ['initial_sympt1', 'initial_sympt2', 'initial_sympt3']
    for sympt_col in symptom_columns:
        df[sympt_col + '_initial'] = df.apply(
            lambda row: any(row[init_sympt_col] == sympt_col for init_sympt_col in initial_sympt_cols),
            axis=1
        )
    return df


# Load Excel file and properties file
excel_path = '/mnt/data/your_excel_file.xlsx'  # Replace with actual path to your Excel file
properties_file_path = '/mnt/data/properties_file.properties'  # Replace with actual path to properties file

# Load DataFrame
df = get_cached_dataframe(excel_path)

# Load properties file containing categories and symptoms
properties = load_properties_file(properties_file_path)

# Categorize symptoms and mark initial symptoms
categorized_symptoms, uncategorized_symptoms = categorize_symptoms(df, properties)
df = mark_initial_symptoms(df, df.columns)

# Print categorized symptoms
print("Categorized Symptoms:")
print(json.dumps(categorized_symptoms, indent=2))

print("\nUncategorized Symptoms:")
print(uncategorized_symptoms)
