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

    logger.debug(f"Starting country data fetch for {disease_abbrev} - {gene}")
    logger.debug(
        f"Filters: criteria={filter_criteria}, countries={countries}, aao={aao}, mutations={mutations}"
    )

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                logger.debug(f"Processing file: {filename}")
                df = get_cached_dataframe(file_path)
                logger.debug(f"Initial dataframe shape: {df.shape}")

                df = df[df["ensemble_decision"] == "IN"]
                logger.debug(f"After ensemble decision filter: {df.shape}")

                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)
                    logger.debug(f"After applying filters: {df.shape}")

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
                logger.debug(f"After disease and gene filter: {filtered_df.shape}")

                # Log unique countries before filtering
                unique_countries_before = filtered_df["country"].unique()
                logger.debug(
                    f"Unique countries before clinical filter: {unique_countries_before}"
                )

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                ]
                logger.debug(
                    f"After clinical and pathogenicity filters: {filtered_df.shape}"
                )

                # Log unique countries after filtering
                unique_countries_after = filtered_df["country"].unique()
                logger.debug(
                    f"Unique countries after all filters: {unique_countries_after}"
                )

                if len(filtered_df) > 0:
                    total_count += len(filtered_df)

                    # Process country data
                    for _, row in filtered_df.iterrows():
                        country = row["country"]
                        if pd.notna(country) and country != -99 and country != "-99":
                            country_counts[country] = country_counts.get(country, 0) + 1
                        else:
                            missing_count += 1

                    logger.debug(f"Current country counts: {country_counts}")
                    logger.debug(f"Current missing count: {missing_count}")

            except Exception as e:
                logger.error(
                    f"Error processing file {filename}: {str(e)}", exc_info=True
                )
                continue

    logger.info(f"Final country counts: {country_counts}")
    logger.info(f"Total count: {total_count}, Missing count: {missing_count}")
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
    try:
        logger.info("Starting country pie chart generation")
        country_counts, missing_count, total_count = _fetch_country_data(
            disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
        )

        # Log the raw data
        logger.debug(f"Raw country counts: {country_counts}")
        logger.debug(f"Total patients: {total_count}")
        logger.debug(f"Missing count: {missing_count}")

        if not country_counts:
            logger.warning("No country data found")
            return {
                "chart": {"type": "pie"},
                "title": {"text": "No Country Data Available"},
                "series": [{"data": []}],
            }

        # Prepare pie chart data
        pie_chart_data = [
            {"name": str(country), "y": count, "count": count}
            for country, count in country_counts.items()
        ]

        # Sort data by count in descending order
        pie_chart_data.sort(key=lambda x: x["count"], reverse=True)

        # Calculate percentages and assign colors
        total = sum(item["count"] for item in pie_chart_data)
        for i, item in enumerate(pie_chart_data):
            item["y"] = (item["count"] / total) * 100
            item["color"] = CHART_COLORS[i] if i < len(CHART_COLORS) else None

        # Calculate missing percentage
        missing_percentage = (
            (missing_count / total_count * 100) if total_count > 0 else 0
        )

        logger.debug(f"Prepared data points: {len(pie_chart_data)}")
        logger.debug(f"First few data points: {pie_chart_data[:3]}")

        chart_config = {
            "chart": {"type": "pie"},
            "accessibility": {"enabled": False},
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

        logger.info("Successfully generated country pie chart")
        return chart_config

    except Exception as e:
        logger.error("Error generating country pie chart", exc_info=True)
        raise
