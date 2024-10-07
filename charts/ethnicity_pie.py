import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, CHART_COLORS
from collections import Counter
import random

logger = logging.getLogger(__name__)


def generate_ethnicity_pie_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
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
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, None, country, mutation)
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

                # Collect ethnicity data
                if "ethnicity" in filtered_df.columns:
                    ethnicity_data.extend(filtered_df["ethnicity"].dropna().tolist())
                total_count += len(filtered_df)

            except Exception as e:
                logger.error(f"Error processing file {filename}: {str(e)}")
                continue

    logger.info(f"Total ethnicity data points: {len(ethnicity_data)}")

    # Count ethnicities, excluding -99
    ethnicity_counts = Counter(str(e) for e in ethnicity_data if e != -99)

    # Calculate missing data
    missing_count = total_count - sum(ethnicity_counts.values())
    missing_percentage = (missing_count / total_count * 100) if total_count > 0 else 0

    # Prepare pie chart data
    pie_chart_data = [
        {"name": k, "y": v}
        for k, v in ethnicity_counts.items()
        if k.lower() != "unknown"
    ]

    # Add "Unknown" category if present
    unknown_count = ethnicity_counts.get("Unknown", 0) + ethnicity_counts.get(
        "unknown", 0
    )
    if unknown_count > 0:
        pie_chart_data.append({"name": "Unknown", "y": unknown_count})

    # Sort data by value in descending order
    pie_chart_data.sort(key=lambda x: x["y"], reverse=True)

    # Calculate percentages
    total = sum(item["y"] for item in pie_chart_data)
    for item in pie_chart_data:
        item["y"] = (item["y"] / total) * 100

    # Function to generate a random color in hex format (if needed)
    def generate_random_color():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF))

    # Assign colors to pie_chart_data
    pie_chart_data_with_colors = [
        {
            "name": data_point["name"],
            "y": data_point["y"],
            # Use predefined colors, or default to None if there are more data points than colors
            "color": (
                CHART_COLORS[index] if index < len(CHART_COLORS) else None
            ),  # Continue with default color
            # "color": colors[index] if index < len(colors) else generate_random_color()  # Optional random color
        }
        for index, data_point in enumerate(pie_chart_data)
    ]

    # Prepare the chart configuration with the colored data
    chart_config = {
        "chart": {"type": "pie"},
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": "Ethnicity"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.1f}%)"
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
                "data": pie_chart_data_with_colors,
            }
        ],
    }

    return chart_config
