import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, RESPONSE_QUANTIFICATION

logger = logging.getLogger(__name__)


def categorize_levodopa_response(row):
    levodopa_response = str(row["levodopa_response"]).lower()
    response_quantification = str(row["response_quantification"]).lower()

    # If levodopa_response or response_quantification is -99, return None
    # TODO incorrect code, the or response_quantification == "-99" should be removed as it excludes the "Yes, undefined" case
    if levodopa_response == "-99" or response_quantification == "-99":
        return None

    # If levodopa_response is "no", return "No"
    if levodopa_response == "no":
        return "No"

    # Loop through the dictionary to match response_quantification
    for category, keywords in RESPONSE_QUANTIFICATION.items():
        if response_quantification in map(str.lower, keywords):
            return category

    return None  # Default case if nothing matches


def _fetch_levodopa_response(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    levodopa_response_counts = {}
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
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, None, country, mutation)

                filtered_df = df[
                    (df["disease_abbrev"] == disease_abbrev)
                    & (
                        (df["gene1"] == gene)
                        | (df["gene2"] == gene)
                        | (df["gene3"] == gene)
                    )
                ]

                filtered_df = filtered_df[
                    (filtered_df["status_clinical"] != "clinically unaffected")
                    & (filtered_df["pathogenicity1"] != "benign")
                    & (filtered_df["pathogenicity2"] != "benign")
                    & (filtered_df["pathogenicity3"] != "benign")
                ]

                total_count += len(filtered_df)

                # Apply the new categorization
                filtered_df["levodopa_category"] = filtered_df.apply(
                    categorize_levodopa_response, axis=1
                )

                # Count responses, excluding None (which includes -99 cases)
                levodopa_response_data = (
                    filtered_df["levodopa_category"].value_counts().to_dict()
                )
                for response, count in levodopa_response_data.items():
                    if response is not None:
                        levodopa_response_counts[response] = (
                            levodopa_response_counts.get(response, 0) + count
                        )
                    else:
                        missing_count += count

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return levodopa_response_counts, missing_count, total_count


def generate_levodopa_response(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    levodopa_response_counts, missing_count, total_count = _fetch_levodopa_response(
        disease_abbrev, gene, filter_criteria, country, mutation, directory
    )

    # Calculate missing percentage
    missing_percentage = (missing_count / total_count * 100) if total_count > 0 else 0

    # Prepare bar chart data
    # Ensure the categories are in the desired order
    category_order = [
        "Good",
        "Moderate",
        "Minimal",
        "Yes, undefined",
        "No",
        "Not treated",
    ]
    categories = [cat for cat in category_order if cat in levodopa_response_counts]
    data = [levodopa_response_counts.get(cat, 0) for cat in categories]

    # Prepare the chart configuration
    chart_config = {
        "chart": {"type": "column"},
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": "Levodopa response"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.2f}%)"
        },
        "xAxis": {"categories": categories, "title": {"text": "Levodopa response"}},
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "series": [
            {"name": "Patients", "data": data, "color": "#AC202D"}  # Dark red color
        ],
    }

    return chart_config
