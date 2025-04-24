import pandas as pd
import os
import logging
from utils import fetch_treatment_response_data
import numpy as np

logger = logging.getLogger(__name__)

def generate_treatment_response_chart(
    genes,
    filter_criteria=None,
    aao=None,
    countries=None,
    mutations=None,
    directory="excel",
):
    """
    Generate a bar chart for treatment response across different genes.

    Parameters:
    - genes: List of genes to include
    - filter_criteria, aao, countries, mutations: Filtering parameters
    - directory: Directory containing Excel files

    Returns:
    - Chart configuration
    """
    treatment_data = fetch_treatment_response_data(genes, filter_criteria, aao, countries, mutations, directory)

    if not any(treatment_data.values()):
        logger.warning(f"No valid treatment response data found for genes: {genes}")
        return None

    # Get all treatment columns that have data
    all_treatments = set()
    for gene_data in treatment_data.values():
        all_treatments.update(gene_data.keys())

    all_treatments = sorted(list(all_treatments))

    # Identify treatments that only have unknown responses
    unknown_only_treatments = []
    valid_treatments = []

    for treatment in all_treatments:
        positive_count = sum(gene_data.get(treatment, {}).get("positive", 0) for gene_data in treatment_data.values())
        negative_count = sum(gene_data.get(treatment, {}).get("negative", 0) for gene_data in treatment_data.values())
        none_count = sum(gene_data.get(treatment, {}).get("none", 0) for gene_data in treatment_data.values())
        temporary_count = sum(gene_data.get(treatment, {}).get("temporary", 0) for gene_data in treatment_data.values())
        partial_count = sum(gene_data.get(treatment, {}).get("partial", 0) for gene_data in treatment_data.values())
        unknown_count = sum(gene_data.get(treatment, {}).get("unknown", 0) for gene_data in treatment_data.values())

        # Check if this treatment only has unknown responses
        if (positive_count + negative_count + none_count + temporary_count + partial_count == 0) and unknown_count > 0:
            # Format the treatment name for display in subtitle
            # For all standard treatment columns (ending with _response), replace "_" with spaces
            display_name = treatment.replace("_response", "")
            if not display_name.startswith("other_drug"):  # Not from other_drug_response column
                display_name = display_name.replace("_", " ")
            unknown_only_treatments.append(display_name)
        else:
            valid_treatments.append(treatment)

    # Format treatment names for display (only for valid treatments)
    display_treatments = []
    for treatment in valid_treatments:
        # For all standard treatment columns (ending with _response), replace "_" with spaces
        display_name = treatment.replace("_response", "")
        if not display_name.startswith("other_drug"):  # Not from other_drug_response column
            display_name = display_name.replace("_", " ")
        display_treatments.append(display_name)

    # Create series for each response type (only for valid treatments)
    positive_data = []
    negative_data = []
    none_data = []
    temporary_data = []
    partial_data = []
    unknown_data = []

    for treatment in valid_treatments:
        positive_count = sum(gene_data.get(treatment, {}).get("positive", 0) for gene_data in treatment_data.values())
        negative_count = sum(gene_data.get(treatment, {}).get("negative", 0) for gene_data in treatment_data.values())
        none_count = sum(gene_data.get(treatment, {}).get("none", 0) for gene_data in treatment_data.values())
        temporary_count = sum(gene_data.get(treatment, {}).get("temporary", 0) for gene_data in treatment_data.values())
        partial_count = sum(gene_data.get(treatment, {}).get("partial", 0) for gene_data in treatment_data.values())
        unknown_count = sum(gene_data.get(treatment, {}).get("unknown", 0) for gene_data in treatment_data.values())

        positive_data.append(int(positive_count))
        negative_data.append(int(negative_count))
        none_data.append(int(none_count))
        temporary_data.append(int(temporary_count))
        partial_data.append(int(partial_count))
        unknown_data.append(int(unknown_count))

    # Create subtitle text with unknown-only treatments
    subtitle_text = ""
    if unknown_only_treatments:
        subtitle_text = "Treatments with only unknown responses: " + ", ".join(unknown_only_treatments)

    chart_config = {
        "accessibility": {
            "enabled": False,
        },
        "chart": {"type": "column"},
        "title": {"text": "Response to Treatment"},
        "subtitle": {"text": subtitle_text},
        "xAxis": {
            "categories": display_treatments,
            "title": {"text": "Treatment"},
        },
        "yAxis": {
            "title": {"text": "Number of Patients"},
            "min": 0,
        },
        "plotOptions": {
            "column": {
                "groupPadding": 0.1,
                "pointPadding": 0.05,
                "borderWidth": 0,
            }
        },
        "tooltip": {},
        "series": [
            {"name": "Positive", "data": positive_data, "color": "#2f7ed8"},
            {"name": "Negative", "data": negative_data, "color": "#0d233a"},
            {"name": "None", "data": none_data, "color": "#8bbc21"},
            {"name": "Temporary", "data": temporary_data, "color": "#910000"},
            {"name": "Partial", "data": partial_data, "color": "#f28f43"},
            {"name": "Unknown", "data": unknown_data, "color": "#1aadce"},
        ],
        "credits": {"enabled": False},
    }

    return chart_config
