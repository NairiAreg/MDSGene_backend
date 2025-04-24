import re
import pandas as pd
import os
import logging
from utils import fetch_duration_data
import numpy as np

logger = logging.getLogger(__name__)

def generate_duration_chart(
    genes,
    filter_criteria=None,
    aao=None,
    countries=None,
    mutations=None,
    directory="excel",
):
    """
    Generate a clustered column chart config for attack duration categories.

    Categories: Hours, Days, Months
    Series: shortest and longest attack durations per gene.
    """
    data = fetch_duration_data(genes, filter_criteria, aao, countries, mutations, directory)
    if not any(data.values()):
        logger.warning(f"No valid duration data found for genes: {genes}")
        return None

    # Calculate missing data
    total_entries = 0
    missing_entries = 0

    for gene, vals in data.items():
        # Count entries in the main lists
        for duration_type in ["shortest", "longest"]:
            entries = vals.get(duration_type, [])
            total_entries += len(entries)

        # Count entries in the missing data lists
        for duration_type in ["shortest_отсутствует", "longest_отсутствует"]:
            entries = vals.get(duration_type, [])
            missing_entries += len(entries)

    missing_percentage = (missing_entries / (total_entries + missing_entries) * 100) if (total_entries + missing_entries) > 0 else 0

    # 1) Ваши данные
    inner = list(data.values())[0]
    combined = set(inner['shortest']) | set(inner['longest'])

    # 2) Предопределённый порядок от меньшей к большей
    units_order = [
        'second', 'seconds',
        'minute', 'minutes', 'min',
        'hour', 'hours', 'hr',
        'day', 'days',
        'week', 'weeks',
        'month', 'months',
        'year', 'years'
    ]

    # 5) Функция, которая находит индекс по любому варианту вхождения единицы
    synonyms = {
        'seconds': ['sec', r'\b\d+\s*s\b'],
        'minutes': ['min', r'\b\d+\s*m\b'],
        'hours': ['hr', r'\b\d+\s*h\b'],
        'days': ['day', 'days'],
        'weeks': ['week', 'weeks'],
        'months': ['month', 'months'],
        'years': ['year', 'years']
    }

    # Use synonyms.keys as the base for categories
    sorted_units = list(synonyms.keys())

    # 4) Строим словарь «категория → индекс»
    category_to_index = {cat: idx for idx, cat in enumerate(sorted_units)}

    def category_index(text):
        txt = text.lower()
        # ищем по точному названию из sorted_units
        for cat, idx in category_to_index.items():
            if re.search(rf'\b{re.escape(cat)}\b', txt):
                return idx
            # пробуем синонимы/аббревиатуры
            for syn in synonyms.get(cat, []):
                if re.search(syn, txt):
                    return idx
        # дефолтное значение, если ничего не подошло
        return None

    # 6) А теперь считаем счётчики автоматически
    n = len(sorted_units)
    shortest_counts = [0] * n
    longest_counts = [0] * n

    # Calculate counts for all genes
    for gene, vals in data.items():
        for txt in vals.get("shortest", []):
            idx = category_index(txt)
            if idx is not None:
                shortest_counts[idx] += 1
        for txt in vals.get("longest", []):
            idx = category_index(txt)
            if idx is not None:
                longest_counts[idx] += 1

    # Пример вывода
    print("Ordered categories:", sorted_units)
    print("Shortest counts:  ", shortest_counts)
    print("Longest counts:   ", longest_counts)

    # Filter out empty categories (those with zero counts)
    non_empty_indices = [i for i, (s, l) in enumerate(zip(shortest_counts, longest_counts)) if s > 0 or l > 0]
    sorted_units = [sorted_units[i] for i in non_empty_indices]
    shortest_counts = [shortest_counts[i] for i in non_empty_indices]
    longest_counts = [longest_counts[i] for i in non_empty_indices]

    chart_config = {
        "chart": {
            "type": "bar",
            "inverted": True,
        },
        "accessibility": {"enabled": False},
        "title": {"text": "Attack Duration Distribution"},
        "subtitle": {
            "text": f"Number of patients with missing data: {missing_entries} ({missing_percentage:.2f}%)"
        },
        "xAxis": {
            "categories": sorted_units,
            "title": {"text": "Duration Unit"},
            "labels": {"style": {"fontSize": "13px", "fontFamily": "Verdana, sans-serif"}},
        },
        "yAxis": {
            "title": {"text": "Number of Patients"},
            "min": 0,
        },
        "legend": {
            "align": "right",
            "verticalAlign": "top",
            "layout": "vertical",
            "x": -10,
            "y": 50,
        },
        "tooltip": {
            # "shared": True,
            # "useHTML": True,
            # "formatter": {
            #     "__function": """
            #     function() {
            #         var total = this.points.reduce(function(sum, point) {
            #             return sum + point.y;
            #         }, 0);
            #         var tooltip = '<b>' + this.x + '</b><br/>';
            #         this.points.forEach(function(point) {
            #             var percentage = (point.y / total * 100).toFixed(2);
            #             var color = point.series.color;
            #             tooltip += '<span style="color:' + color + '">' + point.series.name + ': ' + point.y + ' (' + percentage + '%)</span><br/>';
            #         });
            #         tooltip += 'Total: ' + total;
            #         return tooltip;
            #     }
            #     """
            # },
        },
        "plotOptions": {
            "series": {
                "stacking": "percent",
                "dataLabels": {
                    "enabled": True,
                    # "formatter": {
                    #     "__function": "function() { if (this.y > 0) { return this.y; } }"
                    # },
                    "style": {"textOutline": "none", "fontWeight": "normal"}
                }
            },
            "bar": {"borderWidth": 0}
        },
        "credits": {"enabled": False},
        "series": [
            {"name": "Shortest Attack", "data": shortest_counts, "color": "#A52A2A"},
            {"name": "Longest Attack",  "data": longest_counts,  "color": "#000080"}
        ],
    }
    return chart_config
