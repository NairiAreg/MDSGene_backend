import json
from typing import List

from fastapi import FastAPI, Query, HTTPException, Form, File, UploadFile
from pydantic import BaseModel

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
from qc.api.gene import gene_excel_file, delete_excel_file
from qc.api.gene.list_genes import get_unique_genes
from qc.api.gene.update_excel_file import update_excel_file_content
from qc.api.symptoms import list_symptoms, symptoms_order
from study_details import get_patients_for_publication
from mutation_details import get_data_for_mutation
import logging
from utils import load_symptom_categories, handle_nan_inf
import httpx
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from pubmed_search_endpoint import fetch_pubmed_summaries
from qc.api.files import get_excel_files_list

# Cache to store PubMed responses, with a 1-hour TTL
pubmed_cache = TTLCache(maxsize=1000, ttl=3600)

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
    # categories_metadata = load_symptom_categories()
    categories = {
        "Movement Disorders": [
            "tremor_rest_sympt",
            "bradykinesia_sympt",
            "rigidity_sympt",
            "postural_instability_sympt",
            "dystonia_sympt",
            "dyskinesia_sympt",
            "ataxia_dysdiadochokinesia_sympt",
        ],
        "Cognitive and Behavioral Symptoms": [
            "cognitive_decline_sympt",
            "impulsive_control_disorder_sympt",
            "anxiety_sympt",
            "depression_sympt",
            "psychotic_sympt",
            "intellectual_disability_sympt",
        ],
        "Autonomic Symptoms": [
            "autonomic_sympt",
            "dysphagia_sympt",
            "olfaction_sympt",
            "hypomimia_sympt",
        ],
        "Sleep Disorders": ["rbd_sympt", "myoclonus_sympt"],
        "Neurological Signs": [
            "primitive_reflexes_sympt",
            "spasticity_pyramidal_signs_sympt",
            "gaze_palsy_sympt",
            "saccadic_abnormalities_sympt",
        ],
        "Motor Complications": [
            "motor_fluctuations_sympt",
            "gait_difficulties_falls_sympt",
            "dysarthria_anarthria_sympt",
        ],
        "Developmental and Seizure Disorders": [
            "development_delay_sympt",
            "seizures_sympt",
        ],
    }
    return categories
    # return categories_metadata


@app.post("/submit_symptoms")
async def submit_symptoms_endpoint(
    age: str = Query(..., description="Age of the patient"),
    symptoms: List[str] = Query(..., description="List of symptoms"),
):
    print(f"Received age: {age}")
    print("Received symptoms:")
    for symptom in symptoms:
        print(f"- {symptom}")

    # Here you can add any additional processing logic if needed

    return {
        "message": "Symptoms submitted successfully",
        "age": age,
        "symptoms": symptoms,
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


@app.get("/api/gene/list_excel_files", response_model=List[str])
async def get_excel_files():
    try:
        # Получаем список файлов с помощью функции из отдельного модуля
        excel_files = get_excel_files_list()

        return JSONResponse(content=excel_files)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/gene/list_genes", response_model=List[str])
async def list_genes():
    try:
        genes = list(get_unique_genes())
        #remove empty strings and numbers
        genes = [gene for gene in genes if isinstance(gene, str) and gene]
        return JSONResponse(content=genes)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/api/gene/update_excel_file")
async def update_excel_file(fileId: str = Form(...), newFile: UploadFile = File(...)):
    if not fileId.endswith(".xlsx"):
        return JSONResponse(status_code=400, content={"error": "Invalid file extension. Only .xlsx files are allowed."})

    try:
        await update_excel_file_content(fileId, newFile)
        return JSONResponse(content={"message": "File updated successfully"})
    except FileNotFoundError:
        return JSONResponse(status_code=404, content={"error": "File not found"})
    except Exception as e:
        logger.error(f"❌ Error updating file {fileId}: {str(e)}")
        logger.exception("Detailed error:")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/gene/list_symptoms")
async def web_list_symptoms(gene_id: str):
    try:
        symptoms = list_symptoms.get_symptoms_for_gene(gene_id)
        return JSONResponse(content=symptoms)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# Определим модель для данных о симптомах, которую клиент отправит на сервер
class SymptomOrder(BaseModel):
    geneName: str
    symptomName: str
    categoryName: str
    order: int


@app.post("/api/gene/set_symptom_order")
async def set_symptoms_order(symptoms: List[SymptomOrder]):
    try:
        # Здесь должна быть ваша логика обновления порядка симптомов
        # Предположим, что `update_symptom_order` - это функция, которая обрабатывает обновление в базе данных
        updated = symptoms_order.update_symptom_order(symptoms)

        if not updated:
            raise HTTPException(status_code=400, detail="Failed to update symptoms order")

        return {"status": "success", "message": "Symptoms order updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/gene/add_new_gene")
async def upload_gene_excel_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No selected file")

    file_path = gene_excel_file.save_file(file)

    return JSONResponse(content={"message": "File uploaded successfully", "file_path": file_path})


@app.delete("/api/gene/delete_excel_file")
async def web_delete_excel_file(file_id: str = Query(..., description="ID of the file to delete")):
    logger.debug(f"Received file_id: {file_id}")
    file_path = f"excel/{file_id}"
    if delete_excel_file.delete(file_path):
        return {"message": "File deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="File not found")
