import pandas as pd
import numpy as np
import os
import json

_dataframe_cache = {}


def get_cached_dataframe(file_path):
    global _dataframe_cache

    file_mod_time = os.path.getmtime(file_path)

    if (
        file_path in _dataframe_cache
        and _dataframe_cache[file_path]["mod_time"] == file_mod_time
    ):
        return _dataframe_cache[file_path]["dataframe"]

    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == ".xlsx":
        engine = "openpyxl"
    elif file_extension.lower() == ".xls":
        engine = "xlrd"
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    df = pd.read_excel(file_path, engine=engine)

    _dataframe_cache[file_path] = {"dataframe": df, "mod_time": file_mod_time}

    return df


def apply_filter(df, filter_criteria, aao, country):
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
        df = df[
            (df["mut1_genotype"] == "het")
            | (df["mut2_genotype"] == "het")
            | (df["mut3_genotype"] == "het")
        ]
    elif filter_criteria == 8:
        df = df[
            (df["mut1_genotype"] == "comp_het")
            | (df["mut2_genotype"] == "comp_het")
            | (df["mut3_genotype"] == "comp_het")
        ]
    elif filter_criteria == 9:
        df = df[
            (df["mut1_genotype"].isin(["hom", "comp_het"]))
            | (df["mut2_genotype"].isin(["hom", "comp_het"]))
            | (df["mut3_genotype"].isin(["hom", "comp_het"]))
        ]

    if country:
        country_map = {
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
            "MDA": "Moldova",
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
        if country in country_map:
            df = df[df["country"] == country_map[country]]

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
