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
    clean_name = symptom_name.replace("_sympt", "").lower()
    for category_name, category_data in categories_metadata.items():
        if clean_name in category_data:
            return category_name
    return "Unknown"


def generate_chart_config(category_name, category_symptoms, categories_metadata, show_unknown=True):
    categories = [
        categories_metadata.get(category_name, {})
        .get(symptom.lower().replace("_sympt", ""), symptom)
        for symptom in category_symptoms.keys()
    ]
    present_data = [
        category_symptoms[symptom]["Present"] for symptom in category_symptoms.keys()
    ]
    absent_data = [
        category_symptoms[symptom]["Absent"] for symptom in category_symptoms.keys()
    ]
    unknown_data = [
        category_symptoms[symptom]["Unknown"] for symptom in category_symptoms.keys()
    ] if show_unknown else []

    series = [
        {
            "name": "Present",
            "data": present_data,
            "color": "#A52A2A",
            "dataLabels": {"style": {"color": "white"}},
            "index": 2,
        },
        {
            "name": "Absent",
            "data": absent_data,
            "color": "#000080",
            "dataLabels": {"style": {"color": "white"}},
            "index": 1,
        }
    ]

    if show_unknown:
        series.append({
            "name": "Unknown",
            "data": unknown_data,
            "color": "#808080",
            "dataLabels": {"style": {"color": "white"}},
            "index": 0,
        })

    return {
        "chart": {
            "type": "bar",
            "inverted": True,
        },
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": category_name},
        "subtitle": {
            "text": "Counts on missing (unreported) signs or symptoms are not displayed.",
        } if not show_unknown else {},
        "caption": {
            "text": "Note: Individual elements of parkinsonism not specified.",
            "align": "left",
            "style": {"fontStyle": "italic"}
        } if category_name == "Motor signs and symptoms" else {},
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
        "credits": {"enabled": False},
        "series": series,
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
    # Проверка на PD и GBA
    is_pd_gba = disease_abbrev == "PARK" and gene == "GBA1"

    categories_metadata = load_symptom_categories("properties", disease_abbrev, gene)

    symptom_data = fetch_symptom_data(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )

    categorized_symptoms = {}
    for symptom_name, symptom_stats in symptom_data.items():
        category = map_symptom_to_category(symptom_name, categories_metadata)
        if category != "Unknown":
            if category not in categorized_symptoms:
                categorized_symptoms[category] = {}
            categorized_symptoms[category][symptom_name] = symptom_stats

    chart_configs = []
    for category_name, category_symptoms in categorized_symptoms.items():
        if category_symptoms:
            chart_configs.append(
                {
                    "name": category_name,
                    "chartConfig": generate_chart_config(
                        category_name,
                        category_symptoms,
                        categories_metadata,
                        show_unknown=not is_pd_gba  # Показываем Unknown только для PD и GBA1
                    ),
                }
            )

    # Создаем словарь с порядковыми номерами из categories_metadata
    category_order = {category: idx for idx, category in enumerate(categories_metadata.keys())}

    # Используем этот порядок для сортировки
    chart_configs.sort(key=lambda x: category_order.get(x["name"], float('inf')))
    return chart_configs