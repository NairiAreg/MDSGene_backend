import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, CHART_COLORS

logger = logging.getLogger(__name__)


def _fetch_country_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
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

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                logger.debug(f"Processing file: {filename}")
                df = get_cached_dataframe(file_path)
                logger.debug(f"Initial dataframe rows: {len(df)}")

                # Ensure all column names are lowercase for consistency
                df.columns = [col.lower() for col in df.columns]

                # Basic filtering
                if "mdsgene_decision" in df.columns:
                    df = df[df["mdsgene_decision"] == "IN"]
                logger.debug(f"After ensemble decision filter: {len(df)} rows")

                # Apply user filters
                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)
                logger.debug(f"After applying filters: {len(df)} rows")

                # Disease and gene filtering
                disease_mask = df["disease_abbrev"] == disease_abbrev
                gene_mask = (
                    (df["gene1"] == gene)
                    | (df["gene2"] == gene)
                    | (df["gene3"] == gene)
                )
                filtered_df = df[disease_mask & gene_mask]
                logger.debug(f"After disease and gene filter: {len(filtered_df)} rows")

                if len(filtered_df) == 0:
                    continue

                # Clinical and pathogenicity filtering
                clinical_mask = (
                    filtered_df["status_clinical"] != "clinically unaffected"
                )
                pathogenicity_mask = (
                    (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                )
                filtered_df = filtered_df[clinical_mask & pathogenicity_mask]

                total_count += len(filtered_df)

                # Process country data
                country_data = filtered_df["country"].value_counts(dropna=False).to_dict()
                logger.debug(f"Country data from file: {country_data}")

                for c, count in country_data.items():
                    # Проверяем только на null/nan значения, так как -99 уже заменены
                    if pd.notna(c):
                        country_counts[c] = country_counts.get(c, 0) + count
                        logger.debug(f"Added {count} patients from country {c}")
                    else:
                        missing_count += count
                        logger.debug(f"Added {count} to missing count (country={c})")

            except KeyError as e:
                if "country" in str(e):
                    logger.debug(f"Columns in {filename}: {df.columns.tolist()}")
                logger.error(f"Error accessing data in file {filename}: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
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
    country_counts, missing_count, total_count = _fetch_country_data(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )

    if not country_counts and total_count == 0:
        return {
            "chart": {"type": "pie"},
            "title": {"text": "No Data Available"},
            "subtitle": {"text": "No matching data found for the selected criteria"},
            "series": [{"data": []}],
        }

    # Prepare pie chart data
    pie_chart_data = [
        {"name": k, "y": v, "count": v} for k, v in country_counts.items()
    ]

    # Sort data by value in descending order and assign colors
    pie_chart_data.sort(key=lambda x: x["count"], reverse=True)

    # Calculate percentages
    total = sum(item["count"] for item in pie_chart_data)
    for i, item in enumerate(pie_chart_data):
        item["y"] = (item["count"] / total) * 100
        item["color"] = CHART_COLORS[i] if i < len(CHART_COLORS) else None

    # Calculate missing percentage
    missing_percentage = (missing_count / total_count * 100) if total_count > 0 else 0

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
        "credits": {"enabled": False},
        "series": [{"name": "Country", "colorByPoint": True, "data": pie_chart_data}],
    }

    return chart_config
