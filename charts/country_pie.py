import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, CHART_COLORS

logger = logging.getLogger(__name__)


def _fetch_country_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    country_counts = {}
    total_count = 0
    missing_count = 0

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = df[df["ensemble_decision"] == "IN"]

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

                total_count += len(filtered_df)

                country_data = filtered_df["country"].value_counts().to_dict()
                for c, count in country_data.items():
                    if c != -99 and pd.notna(c):
                        country_counts[c] = country_counts.get(c, 0) + count
                    else:
                        missing_count += count

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return country_counts, missing_count, total_count


def generate_country_pie_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
    directory: str = "excel",
):
    country_counts, missing_count, total_count = _fetch_country_data(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )

    # Prepare pie chart data
    pie_chart_data = [
        {"name": k, "y": v, "count": v} for k, v in country_counts.items()
    ]

    if not pie_chart_data:
        logger.warning("pie_chart_data is empty. No data to display.")
        return {
            "chart": {"type": "pie"},
            "title": {"text": "No Data Available"},
            "series": [{"data": []}],
        }

    # Sort data by value in descending order
    pie_chart_data.sort(key=lambda x: x["count"], reverse=True)

    # Calculate percentages and assign colors
    total = sum(item["count"] for item in pie_chart_data)
    for i, item in enumerate(pie_chart_data):
        item["y"] = (item["count"] / total) * 100
        item["color"] = CHART_COLORS[i] if i < len(CHART_COLORS) else None

    # Calculate missing percentage
    missing_percentage = (missing_count / total_count * 100) if total_count > 0 else 0
    # Update chart config
    chart_config = {
        "chart": {"type": "pie"},
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": "Country Distribution"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.1f}%)"
        },
        "tooltip": {
            "pointFormat": "<br><b>{point.count}</b> patient(s)",
            "useHTML": True,
        },
        "plotOptions": {
            "pie": {
                "allowPointSelect": True,
                "cursor": "pointer",
                "dataLabels": {
                    "enabled": True,
                    "format": "<b>{point.name}</b>: {point.percentage:.1f} %",
                },
            }
        },
        "series": [
            {
                "name": "Country",
                "colorByPoint": True,
                "data": pie_chart_data,
            }
        ],
    }

    return chart_config
