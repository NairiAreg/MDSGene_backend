import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter
from scipy.stats import describe
import numpy as np

logger = logging.getLogger(__name__)


def _fetch_aao_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    aao_data = []
    total_patients = 0
    missing_count = 0

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                logger.info(
                    f"Processing file: {filename}, Initial DataFrame shape: {df.shape}"
                )

                if "mdsgene_decision" in df.columns:
                    df = df[df["mdsgene_decision"] == "IN"]

                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)

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

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                ]

                total_patients += len(filtered_df)

                # Count missing data (AAO is either NaN or -99)
                missing_mask = filtered_df["aao"].isna() | (filtered_df["aao"] == -99)
                missing_count += missing_mask.sum()

                # Collect valid AAO data
                valid_aao = filtered_df.loc[~missing_mask, "aao"]
                aao_data.extend(valid_aao.tolist())

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue

    logger.info(f"Total patients: {total_patients}")
    logger.info(f"Missing count: {missing_count}")
    logger.info(f"Valid AAO data points: {len(aao_data)}")

    return aao_data, total_patients, missing_count


def generate_aao_histogram(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
    directory: str = "excel",
):
    aao_data, total_patients, missing_count = _fetch_aao_data(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )

    if not aao_data:
        logger.warning(
            f"No valid data found for disease_abbrev: {disease_abbrev}, gene: {gene}"
        )
        return None

    # Calculate statistics
    aao_data.sort()
    stats_by_years = describe(aao_data)

    # Calculate percentiles
    if len(aao_data) >= 4:
        percentiles = np.percentile(aao_data, [25, 50, 75])
        hist_aao_25_percent = round(percentiles[0], 2)
        hist_aao_median = round(percentiles[1], 2)
        hist_aao_75_percent = round(percentiles[2], 2)
    else:
        hist_aao_25_percent = hist_aao_median = hist_aao_75_percent = None

    # Calculate missing percentage
    missing_percentage = (
        (missing_count / total_patients * 100) if total_patients > 0 else 0
    )

    # Group the aao_data into age ranges
    grouped_data = [0] * 10  # Initialize with 10 groups (0-9, 10-19, ..., 90-99)
    for age in aao_data:
        if 0 <= age <= 99:
            group_index = int(age // 10)
            grouped_data[group_index] += 1

    chart_config = {
        "accessibility": {
            "enabled": False,
        },
        "chart": {"type": "column"},
        "title": {"text": "Distribution of age at onset"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.2f}%)",
        },
        "xAxis": {
            "categories": [
                "0 - 9",
                "10 - 19",
                "20 - 29",
                "30 - 39",
                "40 - 49",
                "50 - 59",
                "60 - 69",
                "70 - 79",
                "80 - 89",
                "90 - 99",
            ],
            "title": {"text": "Age at onset"},
        },
        "yAxis": {
            "title": {"text": "Number of patients"},
            "min": 0,
            "max": max(grouped_data),
            "tickInterval": min(max(grouped_data), 50),
        },
        "plotOptions": {
            "column": {
                "color": "#AC202D",
                "groupPadding": 0,
                "pointPadding": 0,
                "borderWidth": 0,
            }
        },
        "tooltip": {
            "headerFormat": "{point.key}<br>",
            "pointFormat": "<b>{point.y}</b> Patients",
            "hideDelay": 0,
            "shared": True,
            "useHTML": True,
        },
        "series": [{"name": "Age distribution", "data": grouped_data}],
        "credits": {"enabled": False},
        "legend": {"enabled": False},
    }

    return chart_config
