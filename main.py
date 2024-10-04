from fastapi import FastAPI, Query
import diseases
import overview
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from mutation_details import get_data_for_mutation
from study_details import get_patients_for_publication
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow your frontend origin
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
):

    unique_studies = overview.get_unique_studies(
        disease_abbrev,
        gene,
        filter_criteria=filter_criteria,
        aao=aao,
        country=countries,
    )

    logger.debug(f"Number of unique studies returned: {len(unique_studies)}")

    return unique_studies


@app.get("/study_designs")
async def study_designs_endpoint(
    pmid_list: str,
    filter_criteria: str = Query(None, description="Filter criteria"),
    aao: str = Query(None, description="Age at onset"),
    country: str = Query(None, description="Country"),
):
    study_designs = overview.get_study_design_for_each_study(
        pmid_list, filter_criteria, aao, country
    )
    return study_designs


@app.get("/number_of_cases")
async def number_of_cases_endpoint(
    pmid_list: str,
    filter_criteria: str = Query(None, description="Filter criteria"),
    aao: str = Query(None, description="Age at onset"),
    country: str = Query(None, description="Country"),
):
    number_of_cases = overview.get_number_of_cases_for_each_study(
        pmid_list, filter_criteria, aao, country
    )
    return number_of_cases


@app.get("/patients_for_publication")
async def patients_for_publication_endpoint(
    disease_abbrev: str,
    gene: str,
    pmid: str,
    filter_criteria: str = Query(None, description="Filter criteria"),
    aao: str = Query(None, description="Age at onset"),
    country: str = Query(None, description="Country"),
):
    patients = get_patients_for_publication(
        disease_abbrev, gene, pmid, filter_criteria, aao, country
    )
    return patients


#добавь еще один endpoint def get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, filter_criteria=None, aao=None, country=None, directory='excel') который получает на вход disease_abbrev, gene, pmid, mut_p, filter_criteria, aao, country и directory и возвращает результат работы функции get_data_for_mutation из mutation_details.py
@app.get("/data_for_mutation")
async def data_for_mutation_endpoint(
    disease_abbrev: str,
    gene: str,
    pmid: str,
    mut_p: str,
    filter_criteria: str = Query(None, description="Filter criteria"),
    aao: str = Query(None, description="Age at onset"),
    country: str = Query(None, description="Country"),
    directory: str = Query('excel', description="Directory")
):
    data = get_data_for_mutation(disease_abbrev, gene, pmid, mut_p, filter_criteria, aao, country, directory)
    return data