import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter
from scipy.stats import describe

logger = logging.getLogger(__name__)

def _fetch_aao_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    aao_data = []

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

                # Only apply the filter if filter_criteria, country, or mutation is provided
                if filter_criteria is not None or country is not None or mutation is not None:
                    df = apply_filter(df, filter_criteria, None, country, mutation)

                # Filter the dataframe based on the given criteria
                filtered_df = pd.concat(
                    [
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene1"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene2"] == gene)
                        ],
                        df[
                            (df["disease_abbrev"] == disease_abbrev)
                            & (df["gene3"] == gene)
                        ],
                    ]
                )

                # Further filter based on clinical status, pathogenicity, and non-null age at onset
                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity"] != "benign")
                    & (filtered_df["aao"].notnull())
                ]

                # Collect age at onset data
                aao_data.extend(filtered_df["aao"].tolist())

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return aao_data

def generate_aao_empirical_distribution(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    aao_data = _fetch_aao_data(disease_abbrev, gene, filter_criteria, country, mutation, directory)

    if not aao_data:
        return None

    aao_data.sort()
    stats_by_years = describe(aao_data)

    histogram_data = []
    start_from_0years = [0, 0]
    histogram_data.append(start_from_0years)
    prev = start_from_0years
    prev_value = -1

    for x in aao_data:
        if prev_value < x:
            prev_value = x
        else:
            continue
        if not (0.0 <= x <= 99.9):
            continue
        pp = (sum(1 for a in aao_data if a <= x) * 100.0) / len(aao_data)
        histogram_data.append([x, prev[1]])
        histogram_data.append([x + 0.1, round(pp, 2)])
        prev = [x + 0.1, round(pp, 2)]

    histogram_data.append([100, prev[1]])

    return {
        "hist_aao_ed_data": histogram_data,
        "hist_aao_25_percent": round(stats_by_years[4][1], 2),
        "hist_aao_75_percent": round(stats_by_years[4][3], 2),
        "hist_aao_median": round(stats_by_years[4][2], 2),
        "hist_range_min_years": stats_by_years[1][0],
        "hist_range_max_years": stats_by_years[1][1]
    }