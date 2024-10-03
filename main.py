from fastapi import FastAPI
import diseases
import overview

from fastapi.openapi.utils import get_openapi

app = FastAPI()

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

#создай мне endpoint


# Add a new endpoint to get the unique studies for a given disease abbreviation and gene
@app.get("/unique_studies/{disease_abbrev}/{gene}")
async def unique_studies_endpoint(disease_abbrev: str, gene: str):
    unique_studies = overview.get_unique_studies(disease_abbrev, gene)
    return unique_studies

# Add a new endpoint to get the study design for each study in a list of PMIDs
@app.get("/study_designs")
async def study_designs_endpoint(pmid_list: str):
    study_designs = overview.get_study_design_for_each_study(pmid_list)
    return study_designs

@app.get("/number_of_cases")
async def number_of_cases_endpoint(pmid_list: str):
    number_of_cases = overview.get_number_of_cases_for_each_study(pmid_list)
    return number_of_cases

#добавь еще один endpoinт для get_unique_studies(disease_abbrev, gene, filter_criteria, aao, country, directory='excel'):
#все параметры кромe disease_abbrev: str, gene: str не обязательные
@app.get("/unique_studies/{disease_abbrev}/{gene}/{filter_criteria}/{aao}/{country}")
async def unique_studies_endpoint(disease_abbrev: str, gene: str, filter_criteria: str = None, aao: str = None, country: str = None):
    unique_studies = overview.get_unique_studies(disease_abbrev, gene, filter_criteria, aao, country)
    return unique_studies
