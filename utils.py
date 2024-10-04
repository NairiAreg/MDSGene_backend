import pandas as pd
import numpy as np
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
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


def apply_filter(df, filter_criteria, aao, country: str):

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

        country_map = [
            "AFG",
            "ALB",
            "DZA",
            "AND",
            "AGO",
            "ATG",
            "ARG",
            "ARM",
            "AUS",
            "AUT",
            "AZE",
            "BHS",
            "BHR",
            "BGD",
            "BRB",
            "BLR",
            "BEL",
            "BLZ",
            "BEN",
            "BTN",
            "BOL",
            "BIH",
            "BWA",
            "BRA",
            "BRN",
            "BGR",
            "BFA",
            "BDI",
            "CPV",
            "KHM",
            "CMR",
            "CAN",
            "CAF",
            "TCD",
            "CHL",
            "CHN",
            "COL",
            "COM",
            "COG",
            "CRI",
            "HRV",
            "CUB",
            "CYP",
            "CZE",
            "DNK",
            "DJI",
            "DMA",
            "DOM",
            "ECU",
            "EGY",
            "SLV",
            "GNQ",
            "ERI",
            "EST",
            "SWZ",
            "ETH",
            "FJI",
            "FIN",
            "FRA",
            "GAB",
            "GMB",
            "GEO",
            "DEU",
            "GHA",
            "GRC",
            "GRD",
            "GTM",
            "GIN",
            "GNB",
            "GUY",
            "HTI",
            "HND",
            "HUN",
            "ISL",
            "IND",
            "IDN",
            "IRN",
            "IRQ",
            "IRL",
            "ISR",
            "ITA",
            "JAM",
            "JPN",
            "JOR",
            "KAZ",
            "KEN",
            "KIR",
            "KWT",
            "KGZ",
            "LAO",
            "LVA",
            "LBN",
            "LSO",
            "LBR",
            "LBY",
            "LIE",
            "LTU",
            "LUX",
            "MDG",
            "MWI",
            "MYS",
            "MDV",
            "MLI",
            "MLT",
            "MHL",
            "MRT",
            "MUS",
            "MEX",
            "FSM",
            "MDA",
            "MCO",
            "MNG",
            "MNE",
            "MAR",
            "MOZ",
            "MMR",
            "NAM",
            "NRU",
            "NPL",
            "NLD",
            "NZL",
            "NIC",
            "NER",
            "NGA",
            "PRK",
            "MKD",
            "NOR",
            "OMN",
            "PAK",
            "PLW",
            "PAN",
            "PNG",
            "PRY",
            "PER",
            "PHL",
            "POL",
            "PRT",
            "QAT",
            "KOR",
            "MDA",
            "SAU",
            "SEN",
            "SRB",
            "SYC",
            "SLE",
            "SGP",
            "SVK",
            "SVN",
            "SLB",
            "SOM",
            "ZAF",
            "ESP",
            "LKA",
            "SDN",
            "SUR",
            "SWE",
            "CHE",
            "SYR",
            "TWN",
            "TJK",
            "TZA",
            "THA",
            "TLS",
            "TGO",
            "TON",
            "TTO",
            "TUN",
            "TUR",
            "TKM",
            "TUV",
            "UGA",
            "UKR",
            "ARE",
            "GBR",
            "USA",
            "URY",
            "UZB",
            "VUT",
            "VAT",
            "VEN",
            "VNM",
            "YEM",
            "ZMB",
            "ZWE",
        ]

        # Split the comma-separated string into a list
        country_list = [c.strip().upper() for c in country.split(",")]
        valid_countries = [c for c in country_list if c in country_map]

        if valid_countries:
            df = df[df["country"].isin(valid_countries)]
        else:
            logger.warning(f"No valid countries found in the provided list: {country}")

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
