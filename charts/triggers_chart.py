import pandas as pd
import os
import logging
from utils import fetch_trigger_data
import numpy as np

logger = logging.getLogger(__name__)

def generate_triggers_chart(
    genes,
    filter_criteria=None,
    aao=None,
    countries=None,
    mutations=None,
    directory="excel",
):
    """
    Generate a stacked-percent inverted bar chart config for triggers.

    X-axis: trigger types
    Series: each raw category value (dynamically from cells)
    Subtitle shows count and percent of missing data
    """
    data = fetch_trigger_data(genes, filter_criteria, aao, countries, mutations, directory)
    if not any(data.values()):
        logger.warning(f"No valid trigger data for genes: {genes}")
        return None

    # Collect all triggers & categories
    all_trigs = sorted({t for gd in data.values() for t in gd})
    all_cats = sorted({c for gd in data.values() for trig in gd.values() for c in trig})

    # Compute missing stats
    total = 0
    missing = 0
    for gd in data.values():
        for trig in all_trigs:
            for cat, cnt in gd.get(trig, {}).items():
                total += cnt
                if cat == 'Missing':
                    missing += cnt
    missing_pct = (missing / total * 100) if total else 0

    # Exclude Missing from series/categories
    cats = [c for c in all_cats if c != 'Missing']

    # Get list of triggers counts
    histogram_data = []
    for idx, cat in enumerate(cats):
        count = [int(sum(gd.get(trig, {}).get(cat, 0) for gd in data.values())) for trig in all_trigs]
        histogram_data.append(
            {
                "trigger": cat,
                "count": count
            }
        )

    chart_config = {
        "chart": {"type": "column"},
        "accessibility": {
            "enabled": False,
        },
        "title": {"text": "Triggers Distribution"},
        "subtitle": {"text": f"Number of patients with missing data: {missing} ({missing_pct:.1f}%)"} if missing else {},
        "xAxis": {
            "categories": [item["trigger"] for item in histogram_data],
            "title": {"text": "Triggers"},
        },
        "caption": {},
        "yAxis": {"min": 0, "title": {"text": "Number of patients"}},
        "plotOptions": {"column": {"dataLabels": {"enabled": True}}},
        "credits": {"enabled": False},
        "series": [{
            "name": "Patients",
            "data": [item["count"] for item in histogram_data],
            "color": '#A52A2A',
        }],
    }
    return chart_config
