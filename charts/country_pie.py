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

    logger.info(
        f"Starting country data fetch with parameters: disease={disease_abbrev}, gene={gene}"
    )
    logger.info(
        f"Filters: criteria={filter_criteria}, countries={countries}, aao={aao}, mutations={mutations}"
    )

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                logger.debug(f"Processing file: {filename}")
                df = get_cached_dataframe(file_path)
                initial_rows = len(df)
                logger.debug(f"Initial dataframe rows: {initial_rows}")

                # Verify required columns exist
                required_columns = [
                    "disease_abbrev",
                    "gene1",
                    "gene2",
                    "gene3",
                    "country",
                    "status_clinical",
                    "pathogenicity1",
                    "pathogenicity2",
                    "pathogenicity3",
                ]
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]
                if missing_columns:
                    logger.error(
                        f"Missing required columns in {filename}: {missing_columns}"
                    )
                    logger.debug(f"Available columns: {df.columns.tolist()}")
                    continue

                # Filter by ensemble_decision
                if "ensemble_decision" in df.columns:
                    df = df[df["ensemble_decision"] == "IN"]
                after_ensemble = len(df)
                logger.debug(f"Rows after ensemble decision filter: {after_ensemble}")

                # Apply user filters
                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)
                    logger.debug(f"Rows after applying user filters: {len(df)}")

                # Filter by disease and gene using boolean masks
                disease_mask = df["disease_abbrev"] == disease_abbrev
                gene_mask = (
                    (df["gene1"] == gene)
                    | (df["gene2"] == gene)
                    | (df["gene3"] == gene)
                )
                filtered_df = df[disease_mask & gene_mask]

                after_disease_gene = len(filtered_df)
                logger.debug(f"Rows after disease/gene filter: {after_disease_gene}")

                if after_disease_gene == 0:
                    logger.debug(f"No matching disease/gene data found in {filename}")
                    continue

                # Apply clinical and pathogenicity filters
                clinical_mask = (
                    filtered_df["status_clinical"] != "clinically unaffected"
                )
                pathogenicity_mask = (
                    (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                )
                filtered_df = filtered_df[clinical_mask & pathogenicity_mask]

                final_rows = len(filtered_df)
                logger.debug(f"Final rows after all filters: {final_rows}")

                if final_rows > 0:
                    total_count += final_rows
                    # Verify country column exists and log its content
                    logger.debug(
                        f"Country column unique values: {filtered_df['country'].unique().tolist()}"
                    )

                    country_data = filtered_df["country"].value_counts().to_dict()
                    for c, count in country_data.items():
                        if pd.notna(c) and c != -99:
                            country_counts[c] = country_counts.get(c, 0) + count
                            logger.debug(f"Added {count} patients from country {c}")
                        else:
                            missing_count += count
                            logger.debug(
                                f"Added {count} to missing count (country={c})"
                            )

            except Exception as e:
                logger.error(
                    f"Error processing file {filename}: {str(e)}", exc_info=True
                )
                continue

    logger.info(f"Final country counts: {country_counts}")
    logger.info(f"Total patients: {total_count}, Missing country data: {missing_count}")
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

        # Prepare pie chart data
        pie_chart_data = [
            {"name": k, "y": v, "count": v} for k, v in country_counts.items()
        ]

        if not pie_chart_data:
            logger.warning("No valid country data found for pie chart")
            return {
                "chart": {"type": "pie"},
                "title": {"text": "No Country Data Available"},
                "subtitle": {
                    "text": f"No data found for {disease_abbrev} - {gene} with current filters"
                },
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
        missing_percentage = (
            (missing_count / total_count * 100) if total_count > 0 else 0
        )

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
        return {
            "chart": {"type": "pie"},
            "title": {"text": "Error Generating Chart"},
            "subtitle": {"text": "An error occurred while processing the data"},
            "series": [{"data": []}],
        }
