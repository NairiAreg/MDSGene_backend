import json
from typing import List, Dict

from fastapi import FastAPI, Query, HTTPException, Form, File, UploadFile, Response
from pydantic import BaseModel

import const
import diseases
import overview
from fastapi.middleware.cors import CORSMiddleware
import symptom_predictor as sp
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

MODEL_PATH = "Model/RF_model.pkl"
SYMPTOM_CATEGORIES_FILES = [
    'properties/symptom_categories_EA_CACNA1A.json',
    'properties/symptom_categories_EA_KCNA1.json',
    'properties/symptom_categories_EA_PDHA1.json',
    'properties/symptom_categories_EA_SLC1A3.json',
    'properties/symptom_categories_PARK_GBA1.json',
    'properties/symptom_categories_PARK_LRRK2.json'
]

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


class PredictionRequest(BaseModel):
    one_subject: list

class SymptomSubmission(BaseModel):
    age: int
    symptoms: List[str]

@app.get("/symptom_categories")
async def get_categories_metadata(
    directory: str = Query(
        "excel",
        description="Directory where categories metadata is stored"
    ),
    categories_filename: str = Query(
        "symptom_categories.json",
        description="Filename of the categories metadata file",
    ),
):
    """
    Endpoint для получения категорий симптомов
    """
    return sp.load_symptom_categories(SYMPTOM_CATEGORIES_FILES)

@app.post("/predict")
async def predict(request: PredictionRequest):
    """
    Endpoint для получения предсказания на основе массива признаков
    """
    try:
        prediction = sp.RF_load_and_predict(MODEL_PATH, request.one_subject)
        prediction_result = sp.get_prediction_result(prediction)
        return {"prediction": prediction_result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/submit_symptoms")
async def submit_symptoms(data: SymptomSubmission):
    """
    Endpoint для отправки симптомов и получения предсказания
    """
    try:
        return sp.process_symptoms_submission(data.dict(), MODEL_PATH)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing symptoms: {str(e)}"
        )

# Эндпоинт для получения рекомендаций по диагнозу на основе симптомов
@app.get("/symptoms_for_diagnosis")
async def symptoms_for_diagnosis_endpoint(
    aao: float = Query(None, description="Age at onset"),
    symptoms: List[str] = Query(None, description="List of selected symptoms"),
):
    """
    Endpoint для получения списка возможных заболеваний на основе возраста и симптомов
    """
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
        # ... остальные заболевания
    ]

    no_matching_diseases = [
        "PARK-LRRK2",
        "PARK-SNCA",
        # ... остальные заболевания без совпадений
    ]

    return {
        "matching_diseases": matching_diseases,
        "no_matching_diseases": no_matching_diseases,
    }

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

