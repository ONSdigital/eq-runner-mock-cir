from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from .main import app, SCHEMAS_PATH

client = TestClient(app)


def test_get_instrument_found():
    """Tests the hash for the en version of test_language returns 200 with valid json"""
    response = client.get(
        "/v2/retrieve_collection_instrument",
        params={
            "guid": "b0ae3c1f-9dd7-dcb2-bca5-9f7558fd2d07",
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert "sections" in response_json
    assert "questionnaire_flow" in response_json
    assert response_json.get("title") == "Test Language Survey"


def test_get_instrument_not_found():
    """Check an invalid guid returns 404"""
    response = client.get(
        "/v2/retrieve_collection_instrument",
        params={
            "guid": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert response.status_code == 404


def test_get_instrument_invalid_uuid():
    """Check that an invalid uuid returns a 422"""
    response = client.get(
        "/v2/retrieve_collection_instrument",
        params={
            "guid": "invalid_uuid",
        },
    )
    assert response.status_code == 422


@pytest.mark.parametrize(
    "parameters",
    [
        {"survey_id": "001", "form_type": "health_demo", "language": "en"},
        {"survey_id": "001", "form_type": "health_demo"},
        {"form_type": "health_demo", "language": "en"},
        {"form_type": "health_demo"},
    ],
)
def test_get_metadata_partial_parameters(parameters):
    """Check that the schema valid for all these parameter combinations is returned"""
    response = client.get(
        "/v2/ci_metadata",
        params=parameters,
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "ci_version": 1,
            "data_version": "0.0.3",
            "form_type": "health_demo",
            "id": "f03eef55-0804-385c-c6a5-b099b483d9b1",
            "language": "en",
            "published_at": "2021-01-01T00:00:00.0000000Z",
            "schema_version": "0.0.1",
            "status": "PUBLISHED",
            "survey_id": "001",
            "title": "Labour Market Survey",
            "description": "Mock description",
            "sds_schema": "",
        },
    ]


def test_get_metadata_no_parameters():
    """Check that no parameters returns metadata for all schemas"""
    response = client.get(
        "/v2/ci_metadata",
    )
    schema_count = len(list(Path(SCHEMAS_PATH).rglob("*.json")))
    assert response.status_code == 200
    assert len(response.json()) == schema_count


def test_get_metadata_not_found():
    """Check no matching metadata returns 404"""
    response = client.get(
        "/v2/ci_metadata",
        params={
            "form_type": "invalid_form_type",
        },
    )
    assert response.status_code == 404
