import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter, load_symptom_categories

logger = logging.getLogger(__name__)


def get_symptom_columns(df):
    return [
        col
        for col in df.columns
        if col.endswith("_sympt") and not col.startswith("initial_")
    ]


def categorize_symptom(value):
    if pd.isna(value) or value == -99:
        return "Unknown"
    elif value == "yes":
        return "Present"
    elif value == "no":
        return "Absent"
    else:
        return "Unknown"


def map_symptom_to_category(symptom_name, categories_metadata):
    # Remove _sympt suffix and convert to lowercase for matching
    clean_name = symptom_name.replace("_sympt", "").lower()

    # Search through each category
    for category_name, category_data in categories_metadata.items():
        # Check if the symptom is in this category
        if clean_name in category_data:
            return category_name

    # If not found in any specific category, return "Unknown"
    return "Unknown"


def generate_chart_config(category_name, symptom_data):
    """Generate chart configuration for a specific category"""
    # Prepare data for the chart
    categories = list(symptom_data.keys())
    present_data = [symptom_data[symptom]["Present"] for symptom in categories]
    absent_data = [symptom_data[symptom]["Absent"] for symptom in categories]
    unknown_data = [symptom_data[symptom]["Unknown"] for symptom in categories]

    return {
        "chart": {
            "type": "bar",
            "inverted": True,
        },
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": f"Signs and symptoms in {category_name}"},
        "xAxis": {
            "categories": categories,
            "labels": {
                "style": {"fontSize": "13px", "fontFamily": "Verdana, sans-serif"},
            },
        },
        "yAxis": {
            "min": 0,
            "max": 100,
            "title": {"text": "Number of patients in percent and absolute numbers"},
            "labels": {"format": "{value}%"},
        },
        "legend": {
            "align": "right",
            "verticalAlign": "top",
            "layout": "vertical",
            "x": -10,
            "y": 50,
        },
        "tooltip": {
            "shared": True,
            "useHTML": True,
            "formatter": {
                "__function": """
                function() {
                    var total = this.points.reduce(function(sum, point) {
                        return sum + point.y;
                    }, 0);
                    var tooltip = '<b>' + this.x + '</b><br/>';
                    this.points.forEach(function(point) {
                        var percentage = (point.y / total * 100).toFixed(2);
                        var color = point.series.color;
                        tooltip += '<span style="color:' + color + '">' + point.series.name + ': ' + point.y + ' (' + percentage + '%)</span><br/>';
                    });
                    tooltip += 'Total: ' + total;
                    return tooltip;
                }
                """
            },
        },
        "plotOptions": {
            "series": {
                "stacking": "percent",
                "dataLabels": {
                    "enabled": True,
                    "formatter": {
                        "__function": "function() { if (this.y > 0) { return this.y; } }"
                    },
                    "style": {"textOutline": "none", "fontWeight": "normal"},
                },
            },
            "bar": {"borderWidth": 0},
        },
        "series": [
            {
                "name": "Present",
                "data": present_data,
                "color": "#A52A2A",
                "dataLabels": {"style": {"color": "white"}},
            },
            {
                "name": "Absent",
                "data": absent_data,
                "color": "#000080",
                "dataLabels": {"style": {"color": "white"}},
            },
            {
                "name": "Unknown",
                "data": unknown_data,
                "color": "#808080",
                "dataLabels": {"style": {"color": "white"}},
            },
        ],
    }


def fetch_symptom_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    symptom_data = {}

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

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

                symptom_columns = get_symptom_columns(filtered_df)

                for column in symptom_columns:
                    symptom_name = column.replace("_sympt", "").capitalize()
                    categorized = (
                        filtered_df[column].apply(categorize_symptom).value_counts()
                    )

                    if symptom_name not in symptom_data:
                        symptom_data[symptom_name] = {
                            "Present": 0,
                            "Absent": 0,
                            "Unknown": 0,
                        }

                    for category, count in categorized.items():
                        symptom_data[symptom_name][category] += count

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}")
                continue

    # Filter out symptoms with zero data
    return {k: v for k, v in symptom_data.items() if sum(v.values()) > 0}


def generate_symptoms_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    # Load symptom categories from JSON
    categories_metadata = load_symptom_categories()

    # Fetch all symptom data
    symptom_data = fetch_symptom_data(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )

    # Group symptoms by category
    categorized_symptoms = {}
    for symptom_name, symptom_stats in symptom_data.items():
        category = map_symptom_to_category(symptom_name, categories_metadata)
        if category not in categorized_symptoms:
            categorized_symptoms[category] = {}
        categorized_symptoms[category][symptom_name] = symptom_stats

    # Generate chart configurations for each category
    chart_configs = []
    for category_name, category_symptoms in categorized_symptoms.items():
        if category_symptoms:  # Only create charts for categories with data
            chart_configs.append(
                {
                    "name": category_name,
                    "chartConfig": generate_chart_config(
                        category_name, category_symptoms
                    ),
                }
            )

    # Sort categories by name for consistent ordering
    chart_configs.sort(key=lambda x: x["name"])

    return chart_configs
