import pandas as pd
import numpy as np
import os
import re
import json
import logging
from difflib import get_close_matches
import math
from collections import OrderedDict
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
_dataframe_cache = {}

# List of expected headers extracted from the provided code
EXPECTED_HEADERS = {
    "PMID",
    "Author, year",
    "study_design",
    "genet_methods",
    "lower_age_limit",
    "upper_age_limit",
    "comments_study",
    "family_ID",
    "individual_ID",
    "disease_abbrev",
    "clinical_info",
    "ethnicity",
    "country",
    "sex",
    "index_pat",
    "famhx",
    "num_het_mut_affected",
    "num_hom_mut_affected",
    "num_het_mut_unaffected",
    "num_hom_mut_unaffected",
    "num_wildtype_affected",
    "num_wildtype_unaffected",
    "status_clinical",
    "aae",
    "aao",
    "duration",
    "age_dx",
    "age_death",
    "hg_version",
    "genome_build",
    "gene1",
    "physical_location1",
    "reference_allele1",
    "observed_allele1",
    "mut1_g",
    "mut1_c",
    "mut1_p",
    "mut1_alias_original",
    "mut1_alias",
    "mut1_genotype",
    "mut1_type",
    "gnomAD1 v2.1.1",
    "gnomAD1 v4.0.0",
    "gene2",
    "physical_location2",
    "reference_allele2",
    "observed_allele2",
    "mut2_g",
    "mut2_c",
    "mut2_p",
    "mut2_alias_original",
    "mut2_alias",
    "mut2_genotype",
    "mut2_type",
    "gnomAD2 v2.1.1",
    "gnomAD2 v4.0.0",
    "gene3",
    "physical_location3",
    "reference_allele3",
    "observed_allele3",
    "mut3_g",
    "mut3_c",
    "mut3_p",
    "mut3_alias",
    "mut3_genotype",
    "mut_3_type",
    "gnomAD3 v2.1.1",
    "gnomAD3 v4.0.0",
    "motor_sympt",
    "parkinsonism_sympt",
    "motor_instrument1",
    "motor_score1",
    "motor_instrument2",
    "motor_score2",
    "NMS_park_sympt",
    "olfaction_sympt",
    "NMS_scale",
    "bradykinesia_sympt",
    "tremor_HP:0001337",
    "tremor_rest_sympt",
    "tremor_action_sympt",
    "tremor_postural_sympt",
    "tremor_dystonic_sympt",
    "rigidity_sympt",
    "postural_instability_sympt",
    "levodopa_response",
    "response_quantification",
    "dyskinesia_sympt",
    "dystonia_sympt",
    "hyperreflexia_sympt",
    "diurnal_fluctuations_sympt",
    "sleep_benefit_sympt",
    "motor_fluctuations_sympt",
    "depression_sympt",
    "depression_scale",
    "anxiety_sympt",
    "anxiety_scale",
    "psychotic_sympt",
    "psychotic_scale",
    "sleep_disorder_sympt",
    "cognitive_decline_sympt",
    "subdomains_cognitive_decline",
    "cognitive_decline_scale",
    "autonomic_sympt",
    "atypical_park_sympt",
    "initial_sympt1",
    "initial_sympt2",
    "initial_sympt3",
    "comments_pat",
    "pathogenicity1",
    "pathogenicity2",
    "pathogenicity3",
    "CADD_1",
    "CADD_2",
    "CADD_3",
    "fun_evidence_pos_1",
    "fun_evidence_pos_2",
    "fun_evidence_pos_3",
    "mdsgene_decision",
    "entry",
    "comment",
}

# List of colors
CHART_COLORS = [
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
    "#ac202d",
    "#434348",
    "#154789",
    "#f7a35c",
    "#187422",
    "#604a7b",
    "#e4d354",
    "#2b908f",
    "#f45b5b",
    "#91e8e1",
]

# Country Mapper
COUNTRIES = {
    "AFG": "Afghanistan",
    "ALB": "Albania",
    "DZA": "Algeria",
    "AND": "Andorra",
    "AGO": "Angola",
    "ATG": "Antigua and Barbuda",
    "ARG": "Argentina",
    "ARM": "Armenia",
    "AUS": "Australia",
    "AUT": "Austria",
    "AZE": "Azerbaijan",
    "BHS": "Bahamas",
    "BHR": "Bahrain",
    "BGD": "Bangladesh",
    "BRB": "Barbados",
    "BLR": "Belarus",
    "BEL": "Belgium",
    "BLZ": "Belize",
    "BEN": "Benin",
    "BTN": "Bhutan",
    "BOL": "Bolivia",
    "BIH": "Bosnia and Herzegovina",
    "BWA": "Botswana",
    "BRA": "Brazil",
    "BRN": "Brunei",
    "BGR": "Bulgaria",
    "BFA": "Burkina Faso",
    "BDI": "Burundi",
    "CPV": "Cabo Verde",
    "KHM": "Cambodia",
    "CMR": "Cameroon",
    "CAN": "Canada",
    "CAF": "Central African Republic",
    "TCD": "Chad",
    "CHL": "Chile",
    "CHN": "China",
    "CHN/KOR": "China or Korea",
    "FRO": "Faroe Islands",
    "COL": "Colombia",
    "COM": "Comoros",
    "COG": "Congo",
    "CRI": "Costa Rica",
    "HRV": "Croatia",
    "CUB": "Cuba",
    "CYP": "Cyprus",
    "CZE": "Czech Republic",
    "DNK": "Denmark",
    "DJI": "Djibouti",
    "DMA": "Dominica",
    "DOM": "Dominican Republic",
    "ECU": "Ecuador",
    "EGY": "Egypt",
    "SLV": "El Salvador",
    "GNQ": "Equatorial Guinea",
    "ERI": "Eritrea",
    "EST": "Estonia",
    "SWZ": "Eswatini",
    "ETH": "Ethiopia",
    "FJI": "Fiji",
    "FIN": "Finland",
    "FRA": "France",
    "GAB": "Gabon",
    "GMB": "Gambia",
    "GEO": "Georgia",
    "DEU": "Germany",
    "GHA": "Ghana",
    "GRC": "Greece",
    "GRD": "Grenada",
    "GTM": "Guatemala",
    "GIN": "Guinea",
    "GNB": "Guinea-Bissau",
    "GUY": "Guyana",
    "HTI": "Haiti",
    "HND": "Honduras",
    "HUN": "Hungary",
    "ISL": "Iceland",
    "IND": "India",
    "IDN": "Indonesia",
    "IRN": "Iran",
    "IRQ": "Iraq",
    "IRL": "Ireland",
    "ISR": "Israel",
    "ITA": "Italy",
    "JAM": "Jamaica",
    "JPN": "Japan",
    "JOR": "Jordan",
    "KAZ": "Kazakhstan",
    "KEN": "Kenya",
    "KIR": "Kiribati",
    "KWT": "Kuwait",
    "KGZ": "Kyrgyzstan",
    "LAO": "Laos",
    "LVA": "Latvia",
    "LBN": "Lebanon",
    "LSO": "Lesotho",
    "LBR": "Liberia",
    "LBY": "Libya",
    "LIE": "Liechtenstein",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MDG": "Madagascar",
    "MWI": "Malawi",
    "MYS": "Malaysia",
    "MDV": "Maldives",
    "MLI": "Mali",
    "MLT": "Malta",
    "MHL": "Marshall Islands",
    "MRT": "Mauritania",
    "MUS": "Mauritius",
    "MEX": "Mexico",
    "FSM": "Micronesia",
    "MDA": "Moldova",
    "MCO": "Monaco",
    "MNG": "Mongolia",
    "MNE": "Montenegro",
    "MAR": "Morocco",
    "MOZ": "Mozambique",
    "MMR": "Myanmar",
    "NAM": "Namibia",
    "NRU": "Nauru",
    "NPL": "Nepal",
    "NLD": "Netherlands",
    "NZL": "New Zealand",
    "NIC": "Nicaragua",
    "NER": "Niger",
    "NGA": "Nigeria",
    "PRK": "North Korea",
    "MKD": "North Macedonia",
    "NOR": "Norway",
    "OMN": "Oman",
    "PAK": "Pakistan",
    "PLW": "Palau",
    "PAN": "Panama",
    "PNG": "Papua New Guinea",
    "PRY": "Paraguay",
    "PER": "Peru",
    "PHL": "Philippines",
    "POL": "Poland",
    "PRT": "Portugal",
    "QAT": "Qatar",
    "KOR": "South Korea",
    "SAU": "Saudi Arabia",
    "SEN": "Senegal",
    "SRB": "Serbia",
    "SYC": "Seychelles",
    "SLE": "Sierra Leone",
    "SGP": "Singapore",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "SLB": "Solomon Islands",
    "SOM": "Somalia",
    "ZAF": "South Africa",
    "ESP": "Spain",
    "LKA": "Sri Lanka",
    "SDN": "Sudan",
    "SUR": "Suriname",
    "SWE": "Sweden",
    "CHE": "Switzerland",
    "SYR": "Syria",
    "TWN": "Taiwan",
    "TJK": "Tajikistan",
    "TZA": "Tanzania",
    "THA": "Thailand",
    "TLS": "Timor-Leste",
    "TGO": "Togo",
    "TON": "Tonga",
    "TTO": "Trinidad and Tobago",
    "TUN": "Tunisia",
    "TUR": "Turkey",
    "TKM": "Turkmenistan",
    "TUV": "Tuvalu",
    "UGA": "Uganda",
    "UKR": "Ukraine",
    "ARE": "United Arab Emirates",
    "GBR": "United Kingdom",
    "USA": "United States",
    "URY": "Uruguay",
    "UZB": "Uzbekistan",
    "VUT": "Vanuatu",
    "VAT": "Vatican City",
    "VEN": "Venezuela",
    "VNM": "Vietnam",
    "YEM": "Yemen",
    "ZMB": "Zambia",
    "ZWE": "Zimbabwe",
}

RESPONSE_QUANTIFICATION = {
    "Good": ["good/excellent", "good/transient", "good", "excellent", "significantly"],
    "Yes, undefined": ["-99"],
    "Minimal": ["minimal/intermittent", "minimal", "intermittent", "poor"],
    "Moderate": ["moderate", "marked"],
    "Not treated": ["not treated"],
}


def get_symptom_translations():
    """Create a flat dictionary of all symptom translations from symptom_categories.json"""
    translations = {}

    try:
        with open("properties/symptom_categories.json", "r") as file:
            categories = json.load(file)

        # Flatten the nested structure and collect all translations
        for category, category_data in categories.items():
            if isinstance(category_data, dict):
                for symptom_key, symptom_name in category_data.items():
                    # Convert to snake_case for matching with column names
                    snake_case_key = (
                        symptom_key.lower().replace(" ", "_").replace(":", "_")
                    )

                    # Store both the original key and the modified version
                    translations[snake_case_key] = {
                        "display_name": symptom_name,
                        "original_key": symptom_key,
                    }
                    # Add _sympt version
                    translations[f"{snake_case_key}_sympt"] = {
                        "display_name": symptom_name,
                        "original_key": symptom_key,
                    }
    except Exception as e:
        logger.error(f"Error loading symptom translations: {str(e)}")
        return {}

    return translations


def translate_column_names(df):
    """Translate symptom column names using the symptom translations"""
    translations = get_symptom_translations()

    # Create a mapping dictionary for column renames
    column_mapping = {}
    for col in df.columns:
        # Remove the _sympt suffix for matching if it exists
        base_col = col[:-6] if col.endswith("_sympt") else col

        # Check if this column should be translated
        if base_col in translations:
            display_name = translations[base_col]["display_name"]
            # Add suffix if it was present in original
            new_col = (
                f"{display_name}_sympt" if col.endswith("_sympt") else display_name
            )
            column_mapping[col] = new_col
        elif col in translations:
            display_name = translations[col]["display_name"]
            new_col = (
                f"{display_name}_sympt" if col.endswith("_sympt") else display_name
            )
            column_mapping[col] = new_col

    # Create a copy of the DataFrame with renamed columns
    if column_mapping:
        # First, create a copy of the DataFrame
        new_df = df.copy()
        # Then rename the columns
        new_df.rename(columns=column_mapping, inplace=True)
        return new_df

    return df


def get_cached_dataframe(file_path):
    global _dataframe_cache

    try:
        file_mod_time = os.path.getmtime(file_path)
        if (
            file_path in _dataframe_cache
            and _dataframe_cache[file_path]["mod_time"] == file_mod_time
        ):
            return _dataframe_cache[file_path]["dataframe"]

        # Извлекаем список генов из имени файла (до первого минуса)
        base_filename = os.path.basename(file_path)
        genes_part = base_filename.split('-')[0]  # берем часть до первого минуса
        valid_genes = [g.upper() for g in genes_part.split('_')]  # разбиваем по подчеркиваниям

        _, file_extension = os.path.splitext(file_path)
        engine = "openpyxl" if file_extension.lower() == ".xlsx" else "xlrd"

        df = pd.read_excel(file_path, engine=engine)

        # Convert all headers to lower case and strip whitespace
        df.columns = df.columns.str.lower().str.strip()

        # Если есть гены для фильтрации, применяем фильтрацию
        if valid_genes:
            # Проверяем каждый ген отдельно
            for i in range(1, 4):
                gene_col = f'gene{i}'
                if gene_col in df.columns:
                    # Преобразуем значения в строки перед применением str.upper()
                    gene_mask = ~df[gene_col].astype(str).fillna('').str.upper().isin(valid_genes)

                    # Определяем связанные колонки только для текущего гена
                    related_columns = [
                    f'gene{i}', f'physical_location{i}', f'reference_allele{i}',
                    f'observed_allele{i}', f'mut{i}_g', f'mut{i}_c', f'mut{i}_p',
                    f'mut{i}_alias_original', f'mut{i}_alias', f'mut{i}_genotype',
                        f'mut{i}_type', f'pathogenicity{i}', f'CADD_{i}',
                        f'gnomad{i} v2.1.1', f'gnomad{i} v4.0.0'
                ]
                    # Фильтруем только существующие колонки
                    existing_columns = [col for col in related_columns if col in df.columns]

                    # Заменяем значения с учетом типа данных
                    for col in existing_columns:
                        if df[col].dtype in ['int64', 'float64']:
                            df.loc[gene_mask, col] = -99
                        else:
                            df.loc[gene_mask, col] = '-99'

        # Сначала обработаем PMID отдельно
        if 'pmid' in df.columns:
            df['pmid'] = df['pmid'].astype(str).str.strip().str.replace(r"\s+", " ")
            df['pmid'] = df['pmid'].replace("-99", None)

        for col in df.columns:
            if col != 'pmid':  # Пропускаем PMID
                try:
                    # Сначала преобразуем в строку и очистим от пробелов
                    df[col] = df[col].astype(str).str.strip().str.replace(r"\s+", " ")

                    # Попробуем преобразовать обратно в числовой тип
                    df[col] = pd.to_numeric(df[col], errors="raise")

                    # Если все значения целые, преобразуем в int
                    if (
                        df[col].dtype == "float64"
                        and df[col].notna().all()
                        and (df[col] % 1 == 0).all()
                    ):
                        df[col] = df[col].astype("int64")

                    # Заменяем -99 на np.nan для числовых колонок
                    if df[col].dtype in ["int64", "float64"]:
                        df[col] = df[col].replace(-99, np.nan)
                except (ValueError, TypeError):
                    # Если не получилось преобразовать в число, оставляем как строку
                    # и заменяем "-99" на None
                    df[col] = df[col].replace("-99", None)

        _dataframe_cache[file_path] = {"dataframe": df, "mod_time": file_mod_time}
        return df

    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise e


def apply_filter(df, filter_criteria, aao, country: str, mutation: str):
    print(
        f"Applying filter with criteria: {filter_criteria}, aao: {aao}, country: {country}, mutation: {mutation}"
    )

    # Helper function to identify compound heterozygous cases
    def has_compound_het(row):
        genes = []
        mutations = []
        genotypes = []

        # First pass: collect all valid mutations for each gene
        for i in range(1, 4):
            gene = row[f"gene{i}"]
            mut = row[f"mut{i}_p"]  # Using protein level mutation
            genotype = row[f"mut{i}_genotype"]

            # Only consider valid entries
            if (
                gene not in ["-99", None]
                and mut not in ["-99", None]
                and genotype not in ["-99", None]
            ):
                genes.append(gene)
                mutations.append(mut)
                genotypes.append(genotype)

        # Second pass: check for compound het cases
        for i in range(len(genes)):
            current_gene = genes[i]
            # Skip if we've already processed this gene
            if current_gene == "-99":
                continue

            # If this mutation is explicitly marked as comp_het, check if there's another mutation in the same gene
            if genotypes[i] == "comp_het":
                # Look for another mutation in the same gene
                for j in range(len(genes)):
                    if i != j and genes[j] == current_gene:
                        return True
                # If we didn't find another mutation in the same gene, ignore this comp_het marking
                continue

            # For het mutations, look for other hets in the same gene
            if genotypes[i] == "het":
                current_mutation = mutations[i]
                # Look for other mutations in the same gene
                for j in range(i + 1, len(genes)):
                    if (
                        genes[j] == current_gene
                        and genotypes[j] == "het"
                        and mutations[j] != current_mutation
                    ):
                        return True

            # Mark this gene as processed
            genes[i] = "-99"

        return False

    if filter_criteria == 1:
        df = df[df["index_pat"] == "yes"]
    elif filter_criteria == 2 and aao is not None:
        df = df[df["aao"] < aao]
    elif filter_criteria == 3 and aao is not None:
        df = df[df["aao"] >= aao]
    elif filter_criteria == 4:
        df = df[df["sex"] == "female"]
    elif filter_criteria == 5:
        df = df[df["sex"] == "male"]
    elif filter_criteria == 6:
        df = df[
            (df["mut1_genotype"] == "hom")
            | (df["mut2_genotype"] == "hom")
            | (df["mut3_genotype"] == "hom")
        ]
    elif filter_criteria == 7:
        # First, create mask for rows with heterozygous mutations
        het_condition = (
            (df["mut1_genotype"] == "het")
            | (df["mut2_genotype"] == "het")
            | (df["mut3_genotype"] == "het")
        )

        # Filter out compound hets
        df = df[het_condition & ~df.apply(has_compound_het, axis=1)]

    elif filter_criteria == 8:
        # Include both explicitly marked compound hets and implicit ones
        # Check comments first
        comments_pat_column = next(
            (col for col in df.columns if col.lower() == "comments_pat"), None
        )

        if comments_pat_column:
            comments_condition = (
                df[comments_pat_column]
                .astype(str)
                .str.contains("compound heterozygous mutation", case=False, na=False)
            )
        else:
            comments_condition = pd.Series(False, index=df.index)

        # Combine explicit genotype condition and implicit compound het detection
        df = df[comments_condition | df.apply(has_compound_het, axis=1)]
    elif filter_criteria == 9:

        def has_hom_or_comp_het(row):
            # Check for homozygous mutations
            for i in range(1, 4):
                if row[f"mut{i}_genotype"] == "hom":
                    return True
            # Check for compound het
            return has_compound_het(row)

        comments_pat_column = next(
            (col for col in df.columns if col.lower() == "comments_pat"), None
        )

        if comments_pat_column:
            comments_condition = (
                df[comments_pat_column]
                .astype(str)
                .str.contains(
                    "compound heterozygous mutation|homozygous mutation",
                    case=False,
                    na=False,
                )
            )
        else:
            comments_condition = pd.Series(False, index=df.index)

        df = df[comments_condition | df.apply(has_hom_or_comp_het, axis=1)]

    if country:
        valid_country_codes = set(COUNTRIES.keys())
        country_list = [c.strip().upper() for c in country.split(",")]
        valid_countries = [c for c in country_list if c in valid_country_codes]

        if valid_countries:
            df = df[df["country"].isin(valid_countries)]

    if mutation:
        mutation_list = [m.strip().lower() for m in mutation.split(",")]
        pathogenicity_condition = (
            df["pathogenicity1"].fillna("").astype(str).str.lower().isin(mutation_list)
            | df["pathogenicity2"]
            .fillna("")
            .astype(str)
            .str.lower()
            .isin(mutation_list)
            | df["pathogenicity3"]
            .fillna("")
            .astype(str)
            .str.lower()
            .isin(mutation_list)
        )

        mutation_columns = [
            "mut1_p",
            "mut2_p",
            "mut3_p",
            "mut1_c",
            "mut2_c",
            "mut3_c",
            "mut1_g",
            "mut2_g",
            "mut3_g",
        ]

        mutation_condition = False
        for col in mutation_columns:
            if col in df.columns:
                mutation_condition |= (
                    df[col].astype(str).str.lower().isin(mutation_list)
                )

        df = df[pathogenicity_condition | mutation_condition]

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
        if isinstance(df, pd.DataFrame):
            value = df[column].iloc[index]
        elif isinstance(df, pd.Series):
            value = df.iloc[index] if column is None else df[column]
        else:
            value = df[column]

        if pd.isna(value):
            return default
        if isinstance(value, (np.integer, np.floating)):
            return value.item()
        return value
    except:
        return default


# Define the function to load the categories metadata
def load_symptom_categories(directory="properties", disease_abbrev=None, gene=None):
    # Construct filename with disease and gene postfix if provided
    base_filename = "symptom_categories"
    if disease_abbrev and gene:
        filename = f"{base_filename}_{disease_abbrev.upper()}_{gene.upper()}.json"
    else:
        filename = f"{base_filename}.json"    # Construct the full path to the categories metadata file

    categories_file_path = os.path.join(directory, filename)

    if os.path.exists(categories_file_path):
        with open(categories_file_path, "r") as file:
            # Load JSON data into an OrderedDict to preserve order
            categories_metadata = json.load(file, object_pairs_hook=OrderedDict)
            # Remove the 'Unknown' category if it exists, preserving order
            categories_metadata.pop("Unknown", None)
    else:
        categories_metadata = OrderedDict()  # Use OrderedDict for an empty dict too

    return categories_metadata


def handle_nan_inf(obj):
    if isinstance(obj, float):
        if math.isnan(obj):
            return "NaN"
        elif math.isinf(obj):
            return "Infinity" if obj > 0 else "-Infinity"
    elif isinstance(obj, dict):
        return {k: handle_nan_inf(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [handle_nan_inf(v) for v in obj]
    return obj


def extract_year(author_year):
    """Extract the year from the author_year string."""
    match = re.search(r"\d{4}", author_year)
    if match:
        return int(match.group())
    return 0  # Default to 0 if no year is found
