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
    validator_version: str
    classifier_type: str
    classifier_value: str
    guid: UUID
    language: str
    published_at: str
    survey_id: str
    title: str
    # schema_name added for launcher use. It is not part of the real CIR output.
    schema_name: str
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
        "status": "PUBLISHED",
        "ci_version": 1,
        "validator_version": "0.0.0",
        "classifier_type": "form_type",
        "classifier_value": schema_json.get("form_type", "0000"),
        "schema_name": schema_name,
    }
    return CiMetadata.model_validate(
        {**mock_data, **schema_json, "guid": guid}, from_attributes=True
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
def get_cir_metadata_v2(
    survey_id: str | None = None,
    classifier_type: str | None = None,
    classifier_value: str | None = None,
    language: str | None = None,
) -> list[CiMetadata]:
    """
    Return metadata objects filtered by any of the params which are provided (all optional).
    Raises not found if no metadata can be found for the given params"""
    metadata_collection, _ = get_schema_data()

    if all(
        param is None
        for param in (survey_id, classifier_type, classifier_value, language)
    ):
        return metadata_collection

    # otherwise filter by the params that have been provided
    if filtered_metadata := [
        metadata
        for metadata in metadata_collection
        if not (
            (survey_id and metadata.survey_id != survey_id)
            or (classifier_type and metadata.classifier_type != classifier_type)
            or (classifier_value and metadata.classifier_value != classifier_value)
            or (language and metadata.language != language)
        )
    ]:
        return filtered_metadata
    raise HTTPException(status_code=404)


@lru_cache(maxsize=1)
def get_instrument_metadata(guid: UUID) -> CiMetadata:
    """Return the CiMetadata object for the given guid, or raise HTTPException if not found"""
    for schema in SCHEMAS_PATH.rglob("*.json"):
        schema_json = json.loads(schema.read_text())
        generated_guid = generate_guid_for_schema(schema.stem, schema_json["language"])
        if generated_guid == guid:
            return get_ci_metadata(guid, schema.stem, schema_json)
    raise HTTPException(status_code=404, detail="Metadata not found for the given guid")


@app.get("/v3/ci_metadata")
def get_cir_metadata_v3(
    guid: UUID,
) -> dict[str, str | int | UUID]:
    """
    Return the metadata object for the given guid as a dict.
    Raises not found if no metadata can be found for the given guid.
    """
    try:
        metadata = get_instrument_metadata(guid)
        return metadata.model_dump()
    except HTTPException as e:
        raise e


@app.get("/v2/retrieve_collection_instrument")
def get_collection_instrument(guid: UUID) -> dict:
    """Return the json schema for the given guid or raises not found"""
    _, schema_map = get_schema_data()
    if schema := schema_map.get(guid):
        return schema
    raise HTTPException(status_code=404)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=5004)
