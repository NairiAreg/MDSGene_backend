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

    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == '.xlsx':
        engine = 'openpyxl'
    elif file_extension.lower() == '.xls':
        engine = 'xlrd'
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

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