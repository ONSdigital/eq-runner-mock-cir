import hashlib
import json
from functools import lru_cache
from pathlib import Path
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydantic.json_schema import SkipJsonSchema

SCHEMAS_PATH = Path(Path(__file__).parent.parent, "schemas")

app = FastAPI()


class CiMetadata(BaseModel):
    """
    Model for collection instrument metadata
    copied from https://github.com/ONSdigital/eq-cir-fastapi/blob/main/app/models/responses.py#L21
    """

    # Required fields
    ci_version: int
    data_version: str
    form_type: str
    id: UUID
    language: str
    published_at: str
    schema_version: str
    status: str
    survey_id: str
    title: str
    description: str
    # Optional fields
    sds_schema: str | SkipJsonSchema[None] = ""


def generate_guid_for_schema(schema_name: str, schema_language: str) -> UUID:
    """schema_name and language together are unique so are suitable for generating a guid"""
    combined_hash = hashlib.sha256(
        f"{schema_language}_{schema_name}".encode("utf-8")
    ).hexdigest()
    return UUID(combined_hash[:32])


def get_ci_metadata(guid: UUID, schema_name: str, schema_json: dict) -> CiMetadata:
    """
    For any fields where runner test schemas may be missing data that is mandatory in the CIR model,
    use a mock value for a more realistic response.
    """
    mock_data = {
        "published_at": "2021-01-01T00:00:00.0000000Z",
        "description": "Mock description",
        "status": "PUBLISHED",
        "ci_version": 1,
    }
    # for the mock, set form type to the schema name for ease of identifying the schema
    schema_json["form_type"] = schema_name
    return CiMetadata.model_validate(
        {**mock_data, **schema_json, "id": guid}, from_attributes=True
    )


@lru_cache(maxsize=1)
def get_schema_data() -> tuple[list[CiMetadata], dict[UUID, dict]]:
    """Generate and cache map of uuids to json schemas and a list of metadata objects for each schema"""
    metadata_collection: list[CiMetadata] = []
    schema_map: dict[UUID, dict] = {}
    for schema in SCHEMAS_PATH.rglob("*.json"):
        schema_json = json.loads(schema.read_text())
        guid = generate_guid_for_schema(schema.stem, schema_json["language"])
        metadata_collection.append(get_ci_metadata(guid, schema.stem, schema_json))
        schema_map[guid] = schema_json
    return metadata_collection, schema_map


@app.get("/v2/ci_metadata")
def get_cir_metadata(
    survey_id: str | None = None,
    form_type: str | None = None,
    language: str | None = None,
    status: str | None = None,
) -> list[CiMetadata]:
    """
    Return metadata objects filtered by any of the params which are provided (all optional).
    Raises not found if no metadata can be found for the given params"""
    metadata_collection, _ = get_schema_data()

    if all(param is None for param in (survey_id, form_type, language, status)):
        return metadata_collection

    # otherwise filter by the params that have been provided
    if filtered_metadata := [
        metadata
        for metadata in metadata_collection
        if not (
            (survey_id and metadata.survey_id != survey_id)
            or (form_type and metadata.form_type != form_type)
            or (language and metadata.language != language)
            or (status and metadata.status != status)
        )
    ]:
        return filtered_metadata
    raise HTTPException(status_code=404)


@app.get("/v2/retrieve_collection_instrument")
def get_collection_instrument(guid: UUID) -> dict:
    """Return the json schema for the given guid or raises not found"""
    _, schema_map = get_schema_data()
    if schema := schema_map.get(guid):
        return schema
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5004)
