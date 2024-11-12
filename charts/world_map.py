from utils import COUNTRIES, CHART_COLORS
import pandas as pd
import os
from collections import Counter
from utils import get_cached_dataframe, apply_filter


def get_mutation_columns(df):
    return [
        col
        for col in df.columns
        if col.startswith("mut") and col.split("_")[-1] in ("g", "c", "p")
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


def generate_world_map_data(all_data):
    country_counts = all_data["country"].value_counts()
    return [
        {
            "name": COUNTRIES.get(country, country),
            "value": int(count),
            "z": int(count),
            "code": country,
        }
        for country, count in country_counts.items()
        if country != -99
        and country != "-99"
        and pd.notna(country)
        and country in COUNTRIES  # Ensure we have a valid country code
    ]


def generate_mutation_data(country_data):
    mutation_counts = Counter()

    # Handle mut1 and mut2
    for i in range(1, 3):
        alias_col = f"mut{i}_alias_original"
        mutation_cols = [f"mut{i}_p", f"mut{i}_c", f"mut{i}_g"]

        for _, row in country_data.iterrows():
            # Get the first valid mutation value from p, c, or g columns
            mutation_value = next(
                (
                    row[col]
                    for col in mutation_cols
                    if pd.notna(row[col]) and row[col] != -99 and row[col] != "-99"
                ),
                None,
            )

            if mutation_value is not None:
                alias = row[alias_col]
                if pd.notna(alias) and alias != -99 and alias != "-99":
                    mutation_counts[alias] += 1
                else:
                    mutation_counts[mutation_value] += 1

    # Handle mut3 separately due to different alias column
    alias_col = "mut3_alias"
    mutation_cols = ["mut3_p", "mut3_c", "mut3_g"]

    for _, row in country_data.iterrows():
        mutation_value = next(
            (
                row[col]
                for col in mutation_cols
                if pd.notna(row[col]) and row[col] != -99 and row[col] != "-99"
            ),
            None,
        )

        if mutation_value is not None:
            alias = row[alias_col]
            if pd.notna(alias) and alias != -99 and alias != "-99":
                mutation_counts[alias] += 1
            else:
                mutation_counts[mutation_value] += 1

    total_mutations = sum(mutation_counts.values())

    if total_mutations == 0:
        return []  # Return an empty list if there are no mutations

    pie_data = [
        {"name": str(mutation), "y": (count / total_mutations) * 100}
        for mutation, count in mutation_counts.most_common(10)
    ]

    if len(mutation_counts) > 10:
        other_count = sum(dict(mutation_counts.most_common()[10:]).values())
        pie_data.append(
            {
                "name": "Other",
                "y": (other_count / total_mutations) * 100,
                "color": "#548b90",  # Set color for "Other" slice
            }
        )

    return pie_data


def generate_world_map_charts_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
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
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)

                all_data = pd.concat([all_data, df])

            except Exception as e:
                print(f"Error reading file {filename}: {str(e)}")
                continue

    world_map_data = generate_world_map_data(all_data)

    # Handle the case where there's no data after filtering
    if not world_map_data:
        return None

    charts_data = {
        "worldMap": {
            "chart": {"map": None},
            "accessibility": {"enabled": False},
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
                    "name": gene,
                    "data": world_map_data,
                    "joinBy": ["iso-a3", "code"],
                    "minSize": "4%",
                    "maxSize": "12%",
                    "color": "rgba(44, 175, 254, 0.5)",
                    "borderColor": "#2CAFFE",
                    "borderWidth": 1,
                    "tooltip": {
                        "pointFormat": "{point.name}: {point.z} patients",
                        "headerFormat": "{series.name}<br>",
                    },
                },
            ],
        },
        "mutations": {},
    }

    # Generate mutation pie charts for each country and sort by patient count
    country_patient_counts = all_data["country"].value_counts()
    sorted_countries = [
        country
        for country in country_patient_counts.index
        if country != -99
        and country != "-99"
        and pd.notna(country)
        and country in COUNTRIES
    ]

    for country_code in sorted_countries:
        country_name = COUNTRIES.get(country_code, country_code)
        country_data = all_data[all_data["country"] == country_code]
        mutation_data = generate_mutation_data(country_data)

        # Only create a chart if there are mutations after filtering out -99
        if mutation_data:
            # Assign colors to pie slices
            for i, data_point in enumerate(mutation_data):
                if i < len(CHART_COLORS):
                    data_point["color"] = CHART_COLORS[i]

            charts_data["mutations"][country_name] = {
                "chart": {"type": "pie"},
                "accessibility": {"enabled": False},
                "title": {
                    "text": f"Mutations in {country_name} (n = {len(country_data)})"
                },
                "series": [{"name": "Mutations", "data": mutation_data}],
                "tooltip": {"pointFormat": "Mutations: <b>{point.y:.1f}%</b>"},
            }

    return charts_data
