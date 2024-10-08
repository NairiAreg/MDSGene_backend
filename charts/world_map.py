import pandas as pd
import os
from collections import Counter
from utils import get_cached_dataframe, apply_filter
import pycountry


def get_mutation_columns(df):
    return [
        col
        for col in df.columns
        if col.startswith("mut") and col.endswith(("_g", "_c", "_p"))
    ]


def process_dataframe(df, disease_abbrev, gene):
    df = df[df["ensemble_decision"] == "IN"]

    filtered_df = pd.concat(
        [
            df[(df["disease_abbrev"] == disease_abbrev) & (df[f"gene{i}"] == gene)]
            for i in range(1, 4)
        ]
    )

    filtered_df = filtered_df[
        (filtered_df["status_clinical"] != "clinically unaffected")
        & ~filtered_df[[f"pathogenicity{i}" for i in range(1, 4)]]
        .isin(["benign"])
        .any(axis=1)
    ]

    return filtered_df


def get_country_code(country_name):
    try:
        return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
    except:
        return None


def generate_world_map_data(all_data):
    country_counts = all_data["country"].value_counts()
    return [
        {
            "name": country,
            "value": int(count),
            "z": int(count),
            "code": country,  # Assuming 'country' is the ISO code. If not, you'll need to map it.
        }
        for country, count in country_counts.items()
        if country != -99
    ]


def generate_mutation_data(country_data):
    mutation_cols = get_mutation_columns(country_data)

    mutations = []
    for col in mutation_cols:
        mutations.extend(country_data[col].dropna().tolist())

    mutation_counts = Counter(mutations)
    total_mutations = sum(mutation_counts.values())

    pie_data = [
        {"name": mutation, "y": count / total_mutations * 100}
        for mutation, count in mutation_counts.most_common(5)
    ]

    if len(mutation_counts) > 5:
        other_count = sum(dict(mutation_counts.most_common()[5:]).values())
        pie_data.append({"name": "Other", "y": other_count / total_mutations * 100})

    return pie_data


def generate_world_map_charts_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    country: str = None,
    mutation: str = None,
    directory: str = "excel",
):
    all_data = pd.DataFrame()

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue  # Skip temporary Excel files

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                df = get_cached_dataframe(file_path)
                df = process_dataframe(df, disease_abbrev, gene)

                if (
                    filter_criteria is not None
                    or country is not None
                    or mutation is not None
                ):
                    df = apply_filter(df, filter_criteria, None, country, mutation)

                all_data = pd.concat([all_data, df])

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    top_countries = all_data["country"].value_counts().nlargest(4).index.tolist()

    world_map_data = generate_world_map_data(all_data)

    charts_data = {
        "worldMap": {
            "chart": {"map": None},  # This will be set to topology in JavaScript
            "title": {"text": f"World map {gene}"},
            "subtitle": {"text": "Click bubbles to select"},
            "mapNavigation": {
                "enabled": True,
                "buttonOptions": {"verticalAlign": "bottom"},
            },
            "colorAxis": {
                "min": 1,
                "max": max(item["value"] for item in world_map_data),
                "type": "logarithmic",
            },
            "series": [
                {
                    "type": "map",
                    "name": "World Map",
                    "enableMouseTracking": False,
                    "showInLegend": False,
                },
                {
                    "type": "mapbubble",
                    "name": "Countries",
                    "data": world_map_data,
                    "joinBy": ["iso-a3", "code"],
                    "minSize": "4%",
                    "maxSize": "12%",
                    "tooltip": {"pointFormat": "{point.name}: {point.z}"},
                },
            ],
        },
        "mutations": {},
    }

    for country in top_countries:
        country_data = all_data[all_data["country"] == country]
        mutation_data = generate_mutation_data(country_data)
        charts_data["mutations"][country] = {
            "chart": {"type": "pie"},
            "title": {
                "text": f"Number of mutations in {country} n = {len(country_data)}"
            },
            "series": [{"name": "Mutations", "data": mutation_data}],
        }

    return charts_data
