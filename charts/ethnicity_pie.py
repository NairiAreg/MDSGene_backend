import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, CHART_COLORS
from collections import Counter

logger = logging.getLogger(__name__)

ancestryMapper = {
    "asian": "Asian",
    "jewish ashkenazi": "Jewish (Ashkenazi)",
    "hispanic": "Hispanic",
    "african ancestry": "African Ancestry",
    "jewish non-ashkenazi/undefined": "Jewish (non-ashkenazi/undefined)",
    "indian ancestry": "Indian Ancestry",
    "mixed/other": "Mixed Other",
    "caucasian": "Caucasian",
    "arab": "Arab",
    "berber": "Berber",
    "sephardi jew": "Sephardi Jew",
}


def map_ethnicity(ethnicity):
    """Helper function to map ethnicity values using ancestryMapper"""
    if pd.isna(ethnicity) or ethnicity == -99:
        logger.debug(f"Skipping invalid ethnicity value: {ethnicity}")
        return None

    # Replace any invisible characters and normalize spaces
    ethnicity_clean = " ".join(str(ethnicity).lower().split())

    # Log the original and cleaned values to debug any invisible characters
    if ethnicity_clean != str(ethnicity).lower():
        logger.debug(f"Cleaned ethnicity value: '{ethnicity}' -> '{ethnicity_clean}'")
        logger.debug(f"Hex representation: {ethnicity_clean.encode('utf-8').hex()}")

    mapped_value = ancestryMapper.get(ethnicity_clean)

    if mapped_value:
        logger.debug(f"Successfully mapped '{ethnicity_clean}' to '{mapped_value}'")
    else:
        logger.warning(
            f"No mapping found for: '{ethnicity_clean}' (original: '{ethnicity}')"
        )
        # Log hex values to see invisible characters
        logger.warning(f"Hex values - original: {str(ethnicity).encode('utf-8').hex()}")
        logger.warning(f"Hex values - cleaned: {ethnicity_clean.encode('utf-8').hex()}")

    return mapped_value or ethnicity


def generate_ethnicity_pie_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    ethnicity_data = []
    total_count = 0

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

                # Safely filter based on ensemble_decision
                if "ensemble_decision" in df.columns:
                    df = df[df["ensemble_decision"] == "IN"]
                logger.info(f"After ensemble_decision filter: {df.shape}")

                # Only apply the filter if filter_criteria, country, or mutation is provided
                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)
                logger.info(f"After apply_filter: {df.shape}")

                # Safely filter based on disease_abbrev and gene
                disease_mask = (
                    df["disease_abbrev"] == disease_abbrev
                    if "disease_abbrev" in df.columns
                    else pd.Series(True, index=df.index)
                )
                gene_mask = (
                    (df["gene1"] == gene)
                    | (df["gene2"] == gene)
                    | (df["gene3"] == gene)
                )
                filtered_df = df[disease_mask & gene_mask]
                logger.info(
                    f"After disease_abbrev and gene filter: {filtered_df.shape}"
                )

                # Safely apply additional filters
                status_mask = (
                    filtered_df["status_clinical"] != "clinically unaffected"
                    if "status_clinical" in filtered_df.columns
                    else pd.Series(True, index=filtered_df.index)
                )
                pathogenicity_mask = (
                    (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                )

                filtered_df = filtered_df[status_mask & pathogenicity_mask]
                logger.info(f"After additional filters: {filtered_df.shape}")

                # Map ethnicities using ancestryMapper and collect data
                if "ethnicity" in filtered_df.columns:
                    mapped_ethnicities = filtered_df["ethnicity"].apply(map_ethnicity)
                    ethnicity_data.extend(mapped_ethnicities.dropna().tolist())
                total_count += len(filtered_df)

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue

    logger.info(f"Total ethnicity data points: {len(ethnicity_data)}")

    # Count mapped ethnicities
    ethnicity_counts = Counter(ethnicity_data)

    # Calculate missing data
    missing_count = total_count - sum(ethnicity_counts.values())
    missing_percentage = (missing_count / total_count * 100) if total_count > 0 else 0

    # Prepare pie chart data
    pie_chart_data = [
        {
            "name": k,
            "y": v,
            "color": CHART_COLORS[i] if i < len(CHART_COLORS) else None,
        }
        for i, (k, v) in enumerate(ethnicity_counts.items())
        if k.lower() != "unknown"
    ]

    # Add "Unknown" category if present
    unknown_count = ethnicity_counts.get("Unknown", 0) + ethnicity_counts.get(
        "unknown", 0
    )
    if unknown_count > 0:
        pie_chart_data.append(
            {
                "name": "Unknown",
                "y": unknown_count,
                "color": (
                    CHART_COLORS[len(pie_chart_data)]
                    if len(pie_chart_data) < len(CHART_COLORS)
                    else None
                ),
            }
        )

    # Sort data by value in descending order
    pie_chart_data.sort(key=lambda x: x["y"], reverse=True)

    # Calculate percentages
    total = sum(item["y"] for item in pie_chart_data)
    for i, item in enumerate(pie_chart_data):
        item["count"] = item["y"]  # Store the original count
        item["y"] = (item["y"] / total) * 100
        item["color"] = CHART_COLORS[i] if i < len(CHART_COLORS) else None

    # Prepare the chart configuration with the colored data
    chart_config = {
        "chart": {"type": "pie"},
        "accessibility": {"enabled": False},
        "title": {"text": "Ethnicity"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.1f}%)"
        },
        "tooltip": {
            "pointFormat": "<b>{point.count}</b> patient(s)",
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
                "name": "Ethnicity",
                "colorByPoint": False,
                "data": pie_chart_data,
            }
        ],
    }

    logger.info(f"Final chart config: {chart_config}")

    return chart_config
