import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, RESPONSE_QUANTIFICATION

logger = logging.getLogger(__name__)


def categorize_levodopa_response(row):
    """Categorize levodopa response based on levodopa_response and response_quantification"""
    levodopa_response = str(row["levodopa_response"]).lower()
    response_quantification = str(row["response_quantification"]).lower()

    # If levodopa_response is -99 or NaN, it's missing data
    if levodopa_response == "-99" or pd.isna(row["levodopa_response"]):
        return None

    # If levodopa_response is "no", return "No"
    if levodopa_response == "no":
        return "No"

    # If levodopa_response is "yes" and response_quantification is -99 or falsy,
    # it's "Yes, undefined"
    if levodopa_response == "yes" and (
        response_quantification == "-99"
        or pd.isna(row["response_quantification"])
        or response_quantification == ""
    ):
        return "Yes, undefined"

    # For "yes" responses with valid quantification
    if levodopa_response == "yes":
        # Loop through the dictionary to match response_quantification
        for category, keywords in RESPONSE_QUANTIFICATION.items():
            if any(keyword.lower() == response_quantification for keyword in keywords):
                return category

    return None  # Default case if nothing matches


def _fetch_levodopa_response(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    countries: str = None,
    aao: float = None,
    mutations: str = None,
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
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)

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

                # Count cases where levodopa_response is missing or -99
                missing_mask = filtered_df["levodopa_response"].isna() | (
                    filtered_df["levodopa_response"] == -99
                )
                missing_count += missing_mask.sum()

                # Apply categorization to all entries
                filtered_df["levodopa_category"] = filtered_df.apply(
                    categorize_levodopa_response, axis=1
                )

                # Count responses, excluding None
                response_counts = (
                    filtered_df["levodopa_category"].value_counts().to_dict()
                )
                for response, count in response_counts.items():
                    if response is not None:
                        levodopa_response_counts[response] = (
                            levodopa_response_counts.get(response, 0) + count
                        )

                logger.debug(f"File {filename}:")
                logger.debug(f"Total patients: {len(filtered_df)}")
                logger.debug(f"Missing responses: {missing_mask.sum()}")
                logger.debug(f"Response counts: {response_counts}")

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    return levodopa_response_counts, missing_count, total_count


def generate_levodopa_response(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    levodopa_response_counts, missing_count, total_count = _fetch_levodopa_response(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
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

    logger.debug(f"Categories: {categories}")
    logger.debug(f"Response counts: {levodopa_response_counts}")
    logger.debug(f"Missing percentage: {missing_percentage:.2f}%")

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
