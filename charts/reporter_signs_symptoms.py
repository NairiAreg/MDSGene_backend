import pandas as pd
import os
import logging
from utils import get_cached_dataframe, apply_filter

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


def fetch_symptom_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    disease_abbrev = disease_abbrev.upper()
    symptom_data = {}

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
    symptom_data = {k: v for k, v in symptom_data.items() if sum(v.values()) > 0}

    return symptom_data


def generate_symptoms_chart(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    symptom_data = fetch_symptom_data(
        disease_abbrev, gene, filter_criteria, country, mutation, directory
    )

    # Mapping of original names to correct names
    name_mapping = {
        "Parkinsonsim": "Parkinsonsim",
        "Motor": "Motor",
        "Bradykinesia": "Bradykinesia",
        "Rigidity": "Rigidity",
        "Tremor": "Tremor (any or unspecified)",
        "Tremor_rest": "Resting tremor",
        "Tremor_action": "Action tremor",
        "Tremor_postural": "Postural tremor",
        "Tremor_dystonic": "Dystonic tremor",
        "Postural_instability": "Postural instability",
        "Dyskinesia": "Dyskinesia",
        "Dystonia": "Dystonia",
        "Hyperreflexia": "Hyperreflexia",
        "Diurnal_fluctuations": "Diurnal fluctuations",
        "Sleep_benefit": "Sleep benefit",
        "Motor_fluctuations": "Motor fluctuations",
        "Non_motor_symptoms": "Non-motor sуmptоms",
        "Hyposmia": "Hyposmia",
        "Depression": "Depression",
        "Anxiety": "Anxiety",
        "Psychotic": "Psychotic",
        "Sleep_disorder": "Sleep disorder",
        "Cognitive_decline": "Cognitive decline",
        "Autonomic_symptoms": "Autonomic sуmptоms",
        "Atypical_park": "Atypical parkinsonism sуmptоms",
    }

    # Prepare data for the chart using the correct names
    categories = [name_mapping.get(symptom, symptom) for symptom in symptom_data.keys()]
    present_data = [symptom_data[symptom]["Present"] for symptom in symptom_data.keys()]
    absent_data = [symptom_data[symptom]["Absent"] for symptom in symptom_data.keys()]
    unknown_data = [symptom_data[symptom]["Unknown"] for symptom in symptom_data.keys()]

    chart_config = {
        "chart": {
            "type": "bar",
            "inverted": True,
        },
        "accessibility": {
            "enabled": False,
        },
        "title": {
            "text": "Signs and symptoms in the category (Reporter signs and symptoms)."
        },
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

    return chart_config
