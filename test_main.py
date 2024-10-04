from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_data_for_mutation_endpoint():
    response = client.get(
        "/data_for_mutation",
        params={
            "disease_abbrev": "ABCD",
            "gene": "GENE1",
            "pmid": "12345",
            "mut_p": "mutation1",
            "filter_criteria": "some_criteria",
            "aao": 30,
            "country": "Country1",
            "directory": "excel"
        }
    )
    assert response.status_code == 200
    assert "data" in response.json()
