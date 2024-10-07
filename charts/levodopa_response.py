import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)


def categorize_levodopa_response(row):
    if row["levodopa_response"] == "yes":
        if row["response_quantification"] == -99:
            return "Yes, undefined"
        elif row["response_quantification"] == "good/excellent":
            return "Good"
        elif row["response_quantification"] == "minimal":
            return "Minimal"
        elif row["response_quantification"] == "moderate":
            return "Moderate"
        else:
            return "Yes, undefined"  # For any other cases
    elif row["levodopa_response"] == "no":
        return "No"
    elif row["levodopa_response"] == "not treated":
        return "Not treated"
    else:
        return None  # This will include cases where levodopa_response is -99 or any other value


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
        "title": {"text": "Levodopa response"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.2f}%)"
        },
        "xAxis": {"categories": categories, "title": {"text": "Levodopa response"}},
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "series": [
            {"name": "Patients", "data": data, "color": "#A52A2A"}  # Dark red color
        ],
    }

    return chart_config
