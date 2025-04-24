import json
from typing import List, Dict

from fastapi import FastAPI, Query, HTTPException, Form, File, UploadFile, Response
from pydantic import BaseModel

import const
import diseases
import overview
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

import utils
from charts.aao_empirical_distribution import generate_aao_empirical_distribution
from charts.aao_histogram import generate_aao_histogram
from charts.country_pie import generate_country_pie_chart
from charts.ethnicity_pie import generate_ethnicity_pie_chart
from charts.reporter_signs_symptoms import generate_symptoms_chart
from charts.initial_signs_symptoms import generate_initial_signs_symptoms
from charts.levodopa_response import generate_levodopa_response
from charts.world_map import generate_world_map_charts_data
from charts.triggers_chart import generate_triggers_chart
from charts.duration_chart import generate_duration_chart
from charts.treatment_response_chart import generate_treatment_response_chart
from study_details import get_patients_for_publication
from mutation_details import get_data_for_mutation
import logging
from utils import load_symptom_categories, handle_nan_inf
import httpx
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from pubmed_search_endpoint import fetch_pubmed_summaries
from functools import wraps
import hashlib

import numpy as np
import joblib  # For saving and loading the model

# Cache to store PubMed responses, with a 1-hour TTL
pubmed_cache = TTLCache(maxsize=1000, ttl=3600)

endpoint_cache = TTLCache(maxsize=150000, ttl=2592000)


def cache_response(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
        cache_key = hashlib.md5(cache_key.encode()).hexdigest()

        if cache_key in endpoint_cache:
            return endpoint_cache[cache_key]

        try:
            response = await func(*args, **kwargs)

            # Only cache successful responses (200-299 status codes)
            if (isinstance(response, Response) and 200 <= response.status_code < 300) or \
                    (isinstance(response, dict) or isinstance(response, list)):  # Handle direct returns
                endpoint_cache[cache_key] = response

            return response

        except Exception as e:
            # Don't cache errors, just propagate them
            raise e

    return wrapper

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Allow your frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # You can specify specific HTTP methods if needed
    allow_headers=["*"],  # You can specify specific headers if needed
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        description="This is a very custom OpenAPI schema",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/disease_abbrev")
async def disease_abbrev_endpoint():
    unique_disease_abbrev = diseases.get_unique_disease_abbrev()
    return unique_disease_abbrev


@app.get("/disease_genes")
async def disease_genes_endpoint():
    disease_genes = diseases.get_disease_and_genes()
    return disease_genes


@app.get("/unique_studies/{disease_abbrev}/{gene}")
@cache_response
async def unique_studies_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(
        None, description="Comma-separated list of countries to filter by"
    ),
    mutations: str = Query(None, description="Carrying mutation"),
):
    unique_studies = overview.get_unique_studies(
        disease_abbrev,
        gene,
        filter_criteria=filter_criteria,
        aao=aao,
        country=countries,
        mutation=mutations,
    )

    # Handle NaN and Inf values
    handled_studies = handle_nan_inf(unique_studies)

    return handled_studies


@app.get("/patients_for_publication")
async def patients_for_publication_endpoint(
    disease_abbrev: str,
    gene: str,
    pmid: str,
    filter_criteria: str = Query(None, description="Filter criteria"),
    aao: str = Query(None, description="Age at onset"),
    country: str = Query(None, description="Country"),
    mutation: str = Query(None, description="Mutation"),
):
    patients = get_patients_for_publication(
        disease_abbrev, gene, pmid, filter_criteria, aao, country, mutation
    )
    return patients


@app.get("/data_for_mutation")
@cache_response
async def data_for_mutation_endpoint(
    disease_abbrev: str,
    gene: str,
    pmid: str,
    mut_p: str,
    directory: str = Query("excel", description="Directory"),
):
    data = get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, directory)
    handled_data = handle_nan_inf(data)
    return handled_data


@app.get("/aao_empirical_distribution")
async def aao_empirical_distribution_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_aao_empirical_distribution(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/aao_histogram")
async def aao_histogram_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_aao_histogram(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/country_pie_chart")
async def country_pie_chart_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_country_pie_chart(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/ethnicity_pie_chart")
async def ethnicity_pie_chart_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_ethnicity_pie_chart(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/initial_signs_symptoms")
async def initial_signs_symptoms_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_initial_signs_symptoms(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/levodopa_response")
async def levodopa_response_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_levodopa_response(
        disease_abbrev, gene, filter_criteria, countries, aao, mutations, directory
    )
    return data


@app.get("/reporter_signs_symptoms")
async def reporter_signs_symptoms_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_symptoms_chart(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )
    return data


@app.get("/world_map")
@cache_response
async def generate_world_map_charts_data_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    data = generate_world_map_charts_data(
        disease_abbrev, gene, filter_criteria, aao, countries, mutations, directory
    )
    return data


@app.get("/triggers_chart")
async def triggers_chart_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    gene_list = [gene.strip().upper()]
    data = generate_triggers_chart(
        gene_list, filter_criteria, aao, countries, mutations, directory
    )
    if data is None:
        raise HTTPException(status_code=404, detail="No data found")
    return data


@app.get("/duration_chart")
async def duration_chart_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    gene_list = [gene.strip().upper()]
    data = generate_duration_chart(
        gene_list, filter_criteria, aao, countries, mutations, directory
    )
    if data is None:
        raise HTTPException(status_code=404, detail="No data found")
    return data


@app.get("/treatment_response_chart")
async def treatment_response_chart_endpoint(
    disease_abbrev: str,
    gene: str,
    filter_criteria: int = Query(None, description="Filter criteria"),
    aao: float = Query(None, description="Age at onset"),
    countries: str = Query(None, description="Comma-separated list of countries"),
    mutations: str = Query(None, description="Comma-separated list of mutations"),
    directory: str = Query("excel", description="Directory"),
):
    gene_list = [gene.strip().upper()]
    data = generate_treatment_response_chart(
        gene_list, filter_criteria, aao, countries, mutations, directory
    )
    if data is None:
        raise HTTPException(status_code=404, detail="No data found")
    return data


@app.get("/search_pubmed")
@cache_response
async def search_pubmed(pubmed_ids: str):
    try:
        id_list = [int(id.strip()) for id in pubmed_ids.split(",") if id.strip()]
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid PubMed ID format. Please provide comma-separated integers.",
        )

    if len(id_list) > 200:  # NCBI allows up to 200 IDs per request
        raise HTTPException(
            status_code=400, detail="Maximum 200 PubMed IDs allowed per request"
        )

    if not id_list:
        raise HTTPException(status_code=400, detail="No valid PubMed IDs provided")

    # Check cache for all requested IDs
    cached_results = {
        str(id): pubmed_cache.get(id) for id in id_list if id in pubmed_cache
    }
    missing_ids = [id for id in id_list if str(id) not in cached_results]

    if missing_ids:
        try:
            new_results = await fetch_pubmed_summaries(missing_ids)
            # Update cache with new results
            for id in missing_ids:
                if str(id) in new_results["result"]:
                    pubmed_cache[id] = new_results["result"][str(id)]
                    cached_results[str(id)] = new_results["result"][str(id)]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Ensure the order of results matches the input order
    ordered_results = {str(id): cached_results.get(str(id)) for id in id_list}

    return JSONResponse(content={"result": ordered_results})


def load_symptom_categories(file_paths):
    all_symptoms = {}

    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            for category, symptoms in data.items():
                if category not in all_symptoms:
                    all_symptoms[category] = []
                for symptom_key in symptoms.keys():
                    all_symptoms[category].append(symptom_key)

    # Удаляем дубли и сортируем симптомы в каждой категории
    all_symptoms_cleaned = {category: sorted(list(set(symptoms))) for category, symptoms in all_symptoms.items()}
    return all_symptoms_cleaned

# Endpoint to get the full content of the categories metadata file
@app.get("/symptom_categories")
async def get_categories_metadata(
    directory: str = Query(
        "excel", description="Directory where categories metadata is stored"
    ),
    categories_filename: str = Query(
        "symptom_categories.json",
        description="Filename of the categories metadata file",
    ),
):
    # Load the categories metadata
    # Пример использования
    file_paths = [
        'properties/symptom_categories_EA_CACNA1A.json',
        'properties/symptom_categories_EA_KCNA1.json',
        'properties/symptom_categories_EA_PDHA1.json',
        'properties/symptom_categories_EA_SLC1A3.json',
        'properties/symptom_categories_PARK_GBA1.json',
        'properties/symptom_categories_PARK_LRRK2.json'
    ]

    categories_metadata = load_symptom_categories(file_paths)
    categories = {
        "Motor Signs and Symptoms": [
            "ataxia_sympt",
            "ataxia_ictal_sympt",
            "ataxia_interictal_sympt",
            "limb_ataxia_hp:0002070",
            "limb_ataxia_ictal_sympt",
            "limb_ataxia_interictal_sympt",
            "gait_ataxia_hp:0002066",
            "gait_ataxia_ictal_sympt",
            "gait_ataxia_interictal_sympt",
            "dystonia_hp:0001332",
            "dystonia_ictal_sympt",
            "dystonia_interictal_sympt",
            "hemiplegia_hp:0002301",
            "hemiplegia_ictal_sympt",
            "hemiplegia_interictal_sympt",
            "muscle_weakness_hp:0003324",
            "muscle_weakness_ictal_sympt",
            "muscle_weakness_interictal_sympt",
            "tonic_upgaze_sympt",
            "tonic_upgaze_ictal_sympt",
            "tonic_upgaze_interictal_sympt",
            "choreoathetosis_hp:0001266",
            "choreoathetosis_ictal_sympt",
            "choreoathetosis_interictal_sympt",
            "rigidity_hp:0002063",
            "rigidity_ictal_sympt",
            "rigidity_interictal_sympt",
            "spasticity_hp:0001257",
            "spasticity_ictal_sympt",
            "spasticity_interictal_sympt",
            "muscular_hypotonia_hp:0001252",
            "muscular_hypotonia_ictal_sympt",
            "muscular_hypotonia_interictal_sympt",
            "hypertonia_hp:0001276",
            "hypertonia_ictal_sympt",
            "hypertonia_interictal_sympt",
            "muscle_cramps_sympt",
            "muscle_cramps_ictal_sympt",
            "muscle_cramps_interictal_sympt"
        ],
        "Non-Motor Signs and Symptoms": [
            "cognitive_impairment_hp:0100543",
            "cognitive_impairment_ictal_sympt",
            "cognitive_impairment_interictal_sympt",
            "depression_hp:0000716",
            "depression_ictal_sympt",
            "depression_interictal_sympt",
            "anxiety_sympt",
            "psychotic_sympt",
            "sleep_disorder_sympt"
        ],
        "Paroxysmal Movements": [
            "tremor_hp:0001337",
            "tremor_ictal_sympt",
            "tremor_interictal_sympt",
            "seizures_hp:0001250",
            "seizures_ictal_sympt",
            "seizures_interictal_sympt",
            "dystonia_sympt",
            "dyskinesia_sympt",
            "myoclonus_sympt"
        ],
        "Triggers": [
            "sensitivity_to_alcohol_sympt",
            "emotional_stress_trigger_sympt",
            "physical_stress_trigger_sympt",
            "heat_trigger_sympt",
            "acute_illness_trigger_sympt",
            "fatigue_trigger_sympt",
            "pregnancy_or_hormonal_change_trigger_sympt",
            "sudden_movement_trigger_sympt",
            "caffeine_trigger_sympt",
            "alcohol_trigger_sympt"
        ],
        "Respiratory Symptoms": [
            "respiratory_distress_hp:0002098",
            "respiratory_distress_ictal_sympt",
            "respiratory_distress_interictal_sympt",
            "respiratory_distress_sympt"
        ],
        "Sleep-Related Symptoms": [
            "rbd_sympt",
            "sleep_benefit_sympt"
        ]
    }
    return categories
    # return categories_metadata


def RF_load_and_predict(model_path, one_subject):
    """
    Function to load a trained Random Forest model and make a prediction on a single subject.

    Parameters:
        model_path (str): Path to the saved trained model.
        one_subject (numpy array): Feature array of a single subject to predict.

    Returns:
        prediction (int): Predicted class for the input subject.
    """
    # Load the trained model
    clf = joblib.load(model_path)

    # Ensure the input is in the correct shape for prediction
    one_subject = np.array(one_subject).reshape(1, -1)

    # Make the prediction
    prediction = clf.predict(one_subject)[0]

    return prediction

class PredictionRequest(BaseModel):
    one_subject: list

@app.post("/predict")
async def predict(request: PredictionRequest):
    try:
        model_path = "Model/RF_model.pkl"
        prediction = RF_load_and_predict(model_path, request.one_subject)
        return {"prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# List of all features (used during model training)
ALL_FEATURES = [
"ethnicity",
"country",
"sex",
"aao",
"duration",
"age_dx",
"ataxia_sympt",
"ataxia_ictal_sympt",
"ataxia_interictal_sympt",
"limb_ataxia_hp:0002070",
"limb_ataxia_ictal_sympt",
"limb_ataxia_interictal_sympt",
"gait_ataxia_hp:0002066",
"gait_ataxia_ictal_sympt",
"gait_ataxia_interictal_sympt",
"vertigo_hp:0002321",
"vertigo_ictal_sympt",
"vertigo_interictal_sympt",
"nausea_hp:0002018",
"nausea_ictal_sympt",
"nausea_interictal_sympt",
"dysarthria_hp:0001260",
"dysarthria_ictal_sympt",
"dysarthria_interictal_sympt",
"diplopia_hp:0000651",
"diploplia_ictal_sympt",
"diploplia_interictal_sympt",
"tinnitus_hp:0000360",
"tinnitus_ictal_sympt",
"tinnitus_interictal_sympt",
"dystonia_hp:0001332",
"dystonia_ictal_sympt",
"dystonia_interictal_sympt",
"hemiplegia_hp:0002301",
"hemiplegia_ictal_sympt",
"hemiplegia_interictal_sympt",
"headache_hp:0002315",
"headache_ictal_sympt",
"headache_interictal_sympt",
"migraine_hp:0002076",
"migraine_ictal_sympt",
"migraine_interictal_sympt",
"nystagmus_hp:0000639",
"nystagmus_ictal_sympt",
"nystagmus_interictal_sympt",
"muscle_weakness_hp:0003324",
"muscle_weakness_ictal_sympt",
"muscle_weakness_interictal_sympt",
"fatigue_hp:0012378",
"fatigue_ictal_sympt",
"fatigue_interictal_sympt",
"tonic_upgaze_sympt",
"tonic_upgaze_ictal_sympt",
"tonic_upgaze_interictal_sympt",
"cognitive_impairment_hp:0100543",
"cognitive_impairment_ictal_sympt",
"cognitive_impairment_interictal_sympt",
"subdomain_cognitive_impairment_sympt",
"myokymia_hp:0002411",
"myokymia_ictal_sympt",
"myokymia_interictal_sympt",
"neuromyotonia_ictal_sympt",
"neuromyotonia_interictal_sympt",
"choreoathetosis_hp:0001266",
"choreoathetosis_ictal_sympt",
"choreoathetosis_interictal_sympt",
"visual_blurring_hp:0000622",
"visual_blurring_ictal_sympt",
"visual_blurring_interictal_sympt",
"cerebellar_atrophy_hp:0001272",
"depression_hp:0000716",
"depression_ictal_sympt",
"depression_interictal_sympt",
"rigidity_hp:0002063",
"rigidity_ictal_sympt",
"rigidity_interictal_sympt",
"vomiting_hp:0002013",
"vomiting_ictal_sympt",
"vomiting_interictal_sympt",
"seizures_hp:0001250",
"seizures_ictal_sympt",
"seizures_interictal_sympt",
"tremor_hp:0001337",
"tremor_ictal_sympt",
"tremor_interictal_sympt",
"spasticity_hp:0001257",
"spasticity_ictal_sympt",
"spasticity_interictal_sympt",
"muscular_hypotonia_hp:0001252",
"muscular_hypotonia_ictal_sympt",
"muscular_hypotonia_interictal_sympt",
"hypertonia_hp:0001276",
"hypertonia_ictal_sympt",
"hypertonia_interictal_sympt",
"muscle_cramps_sympt",
"muscle_cramps_ictal_sympt",
"muscle_cramps_interictal_sympt",
"upper_motor_neuron_dysfunction_hp:0002493",
"upper_motor_neuron_dysfunction_ictal_sympt",
"upper_motor_neuron_dysfunction_interictal_sympt",
"muscle_stiffness_hp:0003552",
"muscle_stiffness_hp:0003552_sympt",
"muscle_stiffness_hp:0003552_sympt.1",
"dizziness_hp:0002321",
"dizziness_ictal_sympt",
"dizziness_interictal_sympt",
"skeletal_muscle_hypertrophy_hp:0003712",
"skeletal_muscle_hypertrophy_ictal_sympt",
"skeletal_muscle_hypertrophy_interictal_sympt",
"respiratory_distress_hp:0002098",
"respiratory_distress_ictal_sympt",
"respiratory_distress_interictal_sympt",
"episodic_ataxia_hp:0002131",
"muscle_spasms_hp:0002487",
"cerebellar_ataxia_hp:0001251",
"hand_twitching_sympt",
"slurred_speech_hp:0001350",
"visual_disturbance_sympt",
"leg_rigidity_sympt",
"other_sympt",
"ataxia_hp:0001251",
"dystonia_hp:0007325",
"neuromyotonia_sympt",
"hypermetric_saccade_hp:0007338",
"aphasia_hp:0002381",
"jerking_hp:0001336",
"generalized_hyperreflexia_hp:0007034",
"photophobia_hp:0000613",
"phonophobia_hp:0002183",
"aao_other_sympt",
"fatigue_sympt",
"high_blood_lactate_ictal_sympt",
"high_blood_lactate_interictal_sympt",
"high_csf_lactate_sympt",
"encephalopathy_hp:0001298",
"respiratory_distress_sympt",
"global_development_delay_hp:0001263",
"delayed_motor_skills_hp:0002194",
"delayed_cognitive_dev_sympt",
"axonal_neuropathy_hp:0003477",
"microcephaly_hp:0000252",
"ptosis_hp:0000508",
"ptosis_ictal_sympt",
"ptosis_interictal_sympt",
"dysphagia_sympt",
"tetraparesis_hp:0030182",
"tetraparesis_interictal_sympt",
"areflexia_hp:0001284",
"areflexia_interictal_sympt",
"abnormality_of_skeletal_morphology_hp:0011842",
"osteopenia_hp:0000938",
"short_stature_hp:0004322",
"chorea_hp:0002072",
"intellectual_disability_hp:0001249",
"facial_dysmorphism_hp:0001999",
"mri_brain_abnormality_sympt",
"ophthalmoplegia_hp:0000602",
"ataxia_hp:0002131",
"diplopia_ictal_sympt",
"diplopia_interictal_sympt",
"hyperhidrosis_hp:0000975",
"dysmetric_saccades_hp:0000641",
"ophthalmoparesis_hp:0000597",
"developmental_delay_hp:0001263",
"extensor_plantar_response_hp:0003487",
"motor_developmental_delay_hp:0001270",
"saccadic_smooth_pursuit_hp:0001152",
"slow_saccades_hp:0000514",
"square_wave_jerks_hp:0025402",
"episodic_fever_hp:0001954",
"impaired_vision_hp:0000505",
"decreased_level_of_consciousness_hp:0007185",
"sensory_impairment_hp:0003474",
"coma_hp:0001259",
"sensitivity_to_alcohol_sympt",
"apraxia_hp:0002186",
"emotional_stress_trigger_sympt",
"physical_stress_trigger_sympt",
"heat_trigger_sympt",
"acute_illness_trigger_sympt",
"fatigue_trigger_sympt",
"pregnancy_or_hormonal_change_trigger_sympt",
"sudden_movement_trigger_sympt",
"caffeine_trigger_sympt",
"alcohol_trigger_sympt",
"motor_sympt",
"parkinsonism_sympt",
"nms_park_sympt",
"olfaction_sympt",
"bradykinesia_sympt",
"tremor_rest_sympt",
"tremor_action_sympt",
"tremor_postural_sympt",
"tremor_dystonic_sympt",
"rigidity_sympt",
"postural_instability_sympt",
"dyskinesia_sympt",
"dystonia_sympt",
"hyperreflexia_sympt",
"diurnal_fluctuations_sympt",
"sleep_benefit_sympt",
"motor_fluctuations_sympt",
"depression_sympt",
"anxiety_sympt",
"psychotic_sympt",
"sleep_disorder_sympt",
"cognitive_decline_sympt",
"autonomic_sympt",
"atypical_park_sympt",
"gd_hepatosplenomegaly_sympt",
"gd_blood_abnorm_sympt",
"gd_bone_abnorm_sympt",
"development_delay_sympt",
"tremor_other_sympt",
"gait_difficulties_falls_sympt",
"spasticity_pyramidal_signs_sympt",
"primitive_reflexes_sympt",
"seizures_sympt",
"myoclonus_sympt",
"gaze_palsy_sympt",
"saccadic_abnormalities_sympt",
"ataxia_dysdiadochokinesia_sympt",
"hypomimia_sympt",
"dysarthria_anarthria_sympt",
"rbd_sympt",
"impulsive_control_disorder_sympt",
"hallucinations_sympt",
"intellectual_disability_sympt",
"tremor_unspecified_sympt",
"levodopa_induced_dyskinesia_sympt",
"levodopa_induced_dystonia_sympt"]


# Default value for missing symptoms
DEFAULT_VALUE = 0

# Function to group age into categories (aao_to_value)
def group_age(age: int) -> int:
    if age == -99 or age <= 0:
        return 2
    if age <= 10:
        return 1
    if age <= 20:
        return 3
    if age <= 30:
        return 4
    if age <= 40:
        return 5
    if age <= 50:
        return 6
    if age <= 60:
        return 7
    if age <= 70:
        return 8
    if age <= 80:
        return 9
    if age <= 90:
        return 10
    return 11

# Function to generate the full feature array
def generate_full_feature_array(input_data: Dict[str, int], all_features: List[str], default_value: int) -> List[int]:
    n = len(all_features)
    # Первые 5 элементов - default_value, остальные - 3
    feature_array = [default_value] * min(5, n) + [3] * max(0, n - 5)
    #
    # feature_array = [default_value] * len(all_features)

    for feature, value in input_data.items():
        normalized_feature = feature.replace(" ", "_")  # Replace spaces with underscores

        # Match feature by prefix in all_features
        matching_indices = [i for i, f in enumerate(all_features) if f.startswith(normalized_feature)]

        for index in matching_indices:
            feature_array[index] = value

    return feature_array

# Pydantic model for incoming data
class SymptomSubmission(BaseModel):
    age: int
    symptoms: List[str]

@app.post("/submit_symptoms")
async def submit_symptoms(data: SymptomSubmission):
    # Convert incoming data to a dictionary
    input_data = {"age": group_age(data.age)}  # Group age into categories

    for symptom in data.symptoms:
        normalized_symptom = symptom.replace(" ", "_")  # Normalize symptom names
        input_data[normalized_symptom] = 1  # Mark selected symptoms with 1

    # Generate the full feature array
    full_feature_array = generate_full_feature_array(input_data, ALL_FEATURES, DEFAULT_VALUE)

    model_path = "Model/RF_model.pkl"
    prediction = RF_load_and_predict(model_path, full_feature_array)

    if prediction == 1:
        prediction = "CACNA1A"
    elif prediction == 2:
        prediction = "LRRK2"
    elif prediction == 3:
        prediction = "KCNA1"
    elif prediction == 4:
        prediction = "PDHA1"
    elif prediction == 5:
        prediction = "SLC1A3"
    elif prediction == 6:
        prediction = "GBA1"
    else:
        prediction = "Unknown"
    return {
        "message": "Predicted diagnosis based on symptoms submitted is " + prediction,
        "full_feature_array": full_feature_array,
        "all_features": ALL_FEATURES,
        "prediction": prediction
    }


@app.get("/symptoms_for_diagnosis")
async def symptoms_for_diagnosis_endpoint(
    aao: float = Query(None, description="Age at onset"),
    symptoms: List[str] = Query(None, description="List of selected symptoms"),
):
    # Получить список заболеваний и соответствующих симптомов из модуля diseases
    matching_diseases = diseases.get_matching_diseases(aao=aao, symptoms=symptoms)

    logger.debug(f"Number of matching diseases: {len(matching_diseases)}")

    return matching_diseases


@app.get("/symptoms_for_diagnosis")
async def symptoms_for_diagnosis_endpoint(
    aao: float = Query(None, description="Age at onset"),
    symptoms: List[str] = Query(None, description="List of selected symptoms"),
):
    # Пример данных, которые могут быть возвращены (на основании изображения)
    matching_diseases = [
        {
            "diagnosis": "DYT/PARK-GLB1",
            "n_cases": 28,
            "aao": "Median: 4.0 (Q1: 3.0 - Q3: 16.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Abnormal central motor function (100%)",
                "previously_reported_but_not_selected": "Dystonia (96%), Dysarthria (89%), Abnormality of skeletal morphology (79%)",
                "selected_but_not_previously_reported": "Ataxia/Dysdiadochokinesia (0%)",
            },
            "reported_mutations": "p.Ile51Thr: hom c.1068+1G>T + p.Arg201His: comp. het., p.Ile51Asn: comp. het.",
        },
        {
            "diagnosis": "DYT/PARK-PTS",
            "n_cases": 64,
            "aao": "Median: 0.0 (Q1: 0.0 - Q3: 0.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Abnormal central motor function (81%)",
                "previously_reported_but_not_selected": "Cognitive impairment (78%), Global developmental delay (75%), Intellectual developmental disorder (70%)",
                "selected_but_not_previously_reported": "Ataxia/Dysdiadochokinesia (0%)",
            },
            "reported_mutations": "p.Ile114Val: hom p.Asp136Val + p.Thr67Met: comp. het., p.Val57del + p.Lys29_Ser32del: comp. het.",
        },
        {
            "diagnosis": "DYT/PARK-PLA2G6",
            "n_cases": 115,
            "aao": "Median: 7.0 (Q1: 2.0 - Q3: 24.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Abnormal central motor function (81%)",
                "previously_reported_but_not_selected": "Pyramidal sign (77%), Cerebellar atrophy (69%), MRI brain other abnormalities sympt (59%)",
                "selected_but_not_previously_reported": "Ataxia/Dysdiadochokinesia (0%)",
            },
            "reported_mutations": "p.Ala80Thr: hom p.Val691del: hom p.Arg37* + p.Ser774Ile: comp. het.",
        },
        {
            "diagnosis": "PARK-SYNJ1",
            "n_cases": 17,
            "aao": "Median: 22.0 (Q1: 16.0 - Q3: 28.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Ataxia/Dysdiadochokinesia (24%)",
                "previously_reported_but_not_selected": "Bradykinesia (82%), Tremor (64%), Hyperreflexia (29%)",
                "selected_but_not_previously_reported": "Abnormal central motor function (0%)",
            },
            "reported_mutations": "p.Arg258Gln: hom p.Arg459Pro: hom",
        },
        {
            "diagnosis": "PARK-ATP13A2",
            "n_cases": 36,
            "aao": "Median: 14.5 (Q1: 12.0 - Q3: 17.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Ataxia/Dysdiadochokinesia (86%)",
                "previously_reported_but_not_selected": "Parkinsonism (100%), Bradykinesia (92%), Hypertonia (86%)",
                "selected_but_not_previously_reported": "Abnormal central motor function (0%)",
            },
            "reported_mutations": "p.Gly797Asp: hom p.Gly509Arg: hom",
        },
        {
            "diagnosis": "PARK-CP",
            "n_cases": 26,
            "aao": "Median: 50.5 (Q1: 48.0 - Q3: 53.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Abnormal central motor function (69%)",
                "previously_reported_but_not_selected": "Hypotonia on physical examination (81%), Spastic paraplegia (50%), Diabetes mellitus (39%)",
                "selected_but_not_previously_reported": "Ataxia/Dysdiadochokinesia (0%)",
            },
            "reported_mutations": "p.Trp283Ser: hom c.1864+1G>C: n.a.",
        },
        {
            "diagnosis": "PARK-DCTN1",
            "n_cases": 46,
            "aao": "Median: 49.0 (Q1: 46.0 - Q3: 54.0)",
            "signs_and_symptoms": {
                "selected_and_previously_reported": "Ataxia/Dysdiadochokinesia (100%)",
                "previously_reported_but_not_selected": "Bradykinesia (87%), Resting tremor (58%)",
                "selected_but_not_previously_reported": "Abnormal central motor function (0%)",
            },
            "reported_mutations": "p.Gly174Arg: het p.Ser76Thr: het",
        },
    ]

    # Перечень заболеваний, по которым не было записано никаких выбранных признаков и симптомов
    no_matching_diseases = [
        "PARK-LRRK2",
        "PARK-SNCA",
        "PARK-PINK1",
        "PARK-VPS35",
        "PARK-TOR1A",
        "DYT-KMT2B",
        "DYT-GNAL",
        "DYT-THAP1",
        "DYT-ANO3",
        "PARK-DNKQ",
        "PARK-RFXOX",
        "DYT/PARK-SLC30A10",
        "DYT/PARK-TAF1",
        "DYT/PARK-QDPR",
        "DYT/PARK-SLC6A3",
        "HSP-REEP1",
        "DYT-PRKRA",
        "DYT/PARK-GCH1",
        "DYT-HPCA",
        "PARK-VPS13C",
        "DYT/PARK-TH",
        "DYT-KCTD17",
        "DYT-SGCE",
        "DYT/PARK-SPR",
        "HSP-ATL1",
        "HSP-SPAST",
    ]

    logger.debug(f"Number of matching diseases: {len(matching_diseases)}")

    response = {
        "matching_diseases": matching_diseases,
        "no_matching_diseases": no_matching_diseases,
    }

    return response


@app.post("/ai_prompt")
async def run_ollama_endpoint(prompt: str):
    input_text = """
    You are a model that converts patient information into a JSON format. I will provide you with data about the patient's age and symptoms in plain text, and your task is to return it in a structured JSON format. Here’s an example:

Input data:

Age: 42  
Symptoms:  
- Limb dystonia  
- Bradykinesia  
- Resting tremor  
- Leg rigidity  

Your response should be in the following JSON format:

{
  "age": 42,
  "symptoms": [
    {
      "name": "Limb dystonia",
      "description": "No symptom description provided"
    },
    {
      "name": "Bradykinesia",
      "description": "No symptom description provided"
    },
    {
      "name": "Resting tremor",
      "description": "No symptom description provided"
    },
    {
      "name": "Leg rigidity",
      "description": "No symptom description provided"
    }
  ]
}

Now, using this format, I will provide information about a different patient, and you will convert it into JSON.

Input data:
    """

    extraction_response = utils.run_ollama_model(
        input_text
        + prompt
        + " please return the extracted data in JSON format without any additional text."
    )

    if not extraction_response:
        return {"error": "Failed to extract data from input text."}

    return extraction_response
    # try:
    #     extraction_data = json.loads(extraction_response)
    #     age = extraction_data.get("age")
    #     symptoms = extraction_data.get("symptoms", [])
    # except json.JSONDecodeError:
    #     return {"error": "Failed to parse extraction response."}
    #
    # # Pass extracted data to the diagnosis function
    # response = await symptoms_for_diagnosis_endpoint(aao=age, symptoms=symptoms)
    # if not response:
    #     return {"error": "Failed to process extracted data for diagnosis."}
    #
    # # Send response to Ollama to convert to readable text
    # summary_request = {
    #     "instruction": "Convert the diagnosis information into a readable patient report.",
    #     "data": response
    # }
    # summary_response = api.run_ollama_model(json.dumps(summary_request))
    # if summary_response:
    #     return {"response": summary_response}
    # return {"error": "Failed to generate readable response."}


# def clean_response_from_text(text):
#     # Extract JSON string from the text
#     start = text.find('```json') + len('```json')
#     end = text.find('```', start)
#     json_string = text[start:end].strip()
#
#     return json_string
