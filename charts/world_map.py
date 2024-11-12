from utils import COUNTRIES, CHART_COLORS
import pandas as pd
import os
import logging
from collections import Counter
from utils import get_cached_dataframe, apply_filter

logger = logging.getLogger(__name__)


def process_dataframe(df, disease_abbrev, gene):
    logger.debug(f"Processing dataframe for {disease_abbrev} - {gene}")
    logger.debug(f"Initial shape: {df.shape}")

    df = df[df["ensemble_decision"] == "IN"]
    logger.debug(f"After ensemble filter: {df.shape}")

    filtered_df = pd.concat(
        [
            df[(df["disease_abbrev"] == disease_abbrev) & (df[f"gene{i}"] == gene)]
            for i in range(1, 4)
        ]
    )
    logger.debug(f"After gene filter: {filtered_df.shape}")

    filtered_df = filtered_df[
        (filtered_df["status_clinical"] != "clinically unaffected")
        & ~filtered_df[[f"pathogenicity{i}" for i in range(1, 4)]]
        .isin(["benign"])
        .any(axis=1)
    ]
    logger.debug(f"After clinical and pathogenicity filter: {filtered_df.shape}")

    # Log unique countries
    unique_countries = filtered_df["country"].unique()
    logger.debug(f"Unique countries in filtered data: {unique_countries}")

    return filtered_df


def generate_world_map_data(all_data):
    logger.debug("Generating world map data")
    # Log raw country data
    country_value_counts = all_data["country"].value_counts()
    logger.debug(f"Raw country counts: {country_value_counts}")

    world_map_data = []
    for country, count in country_value_counts.items():
        if (
            pd.notna(country)
            and country != -99
            and country != "-99"
            and country in COUNTRIES
        ):
            entry = {
                "name": COUNTRIES.get(country, country),
                "value": int(count),
                "z": int(count),
                "code": country,
            }
            world_map_data.append(entry)
            logger.debug(f"Added country data: {entry}")
        else:
            logger.debug(f"Skipped country: {country} (count: {count})")

    logger.info(f"Generated {len(world_map_data)} map data points")
    return world_map_data


def generate_world_map_charts_data(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = None,
    aao: float = None,
    countries: str = None,
    mutations: str = None,
    directory: str = "excel",
):
    logger.info(f"Starting world map generation for {disease_abbrev} - {gene}")
    all_data = pd.DataFrame()
    total_patients = 0
    missing_count = 0

    for filename in os.listdir(directory):
        if filename.startswith(".~") or filename.startswith("~$"):
            continue

        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory, filename)
            try:
                logger.debug(f"Processing file: {filename}")
                df = get_cached_dataframe(file_path)
                df = process_dataframe(df, disease_abbrev, gene)

                if (
                    filter_criteria is not None
                    or countries is not None
                    or mutations is not None
                ):
                    df = apply_filter(df, filter_criteria, aao, countries, mutations)

                # Count missing countries
                total_patients += len(df)
                missing_mask = (
                    df["country"].isna()
                    | (df["country"] == -99)
                    | (df["country"] == "-99")
                )
                missing_count += missing_mask.sum()

                all_data = pd.concat([all_data, df])

            except Exception as e:
                logger.error(f"Error reading file {filename}: {str(e)}", exc_info=True)
                continue

    world_map_data = generate_world_map_data(all_data)
    logger.debug(f"Generated world map data: {len(world_map_data)} points")

    if not world_map_data:
        logger.warning("No world map data generated")
        return None

    # Calculate missing percentage
    missing_percentage = (
        (missing_count / total_patients * 100) if total_patients > 0 else 0
    )

    charts_data = {
        "worldMap": {
            "chart": {"map": None},
            "accessibility": {"enabled": False},
            "title": {"text": f"World map {gene}"},
            "subtitle": {
                "text": f"Number of patients with missing data: {missing_count} ({missing_percentage:.2f}%)"
            },
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
