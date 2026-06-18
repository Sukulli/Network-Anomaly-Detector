from __future__ import annotations

import json
from pathlib import Path

from app.main import app
from app.schemas import PredictionRequest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PROJECT_ROOT / "models" / "metadata.json"
SAMPLE_REQUEST_PATH = PROJECT_ROOT / "reports" / "sample_prediction_request.json"
README_PATH = PROJECT_ROOT / "README.md"
RUNTIME_REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
DEV_REQUIREMENTS_PATH = PROJECT_ROOT / "requirements-dev.txt"


def test_sample_prediction_request_matches_api_schema() -> None:
    payload = json.loads(SAMPLE_REQUEST_PATH.read_text(encoding="utf-8"))

    request = PredictionRequest.model_validate(payload)

    assert set(payload) == set(PredictionRequest.model_fields)
    assert request.proto == "udp"
    assert request.service == "-"
    assert request.state == "INT"


def test_metadata_feature_contract_matches_api_schema() -> None:
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    feature_columns = [
        *metadata["numeric_features"],
        *metadata["categorical_features"],
    ]

    assert metadata["dataset"] == "UNSW-NB15"
    assert metadata["task"] == "binary_classification"
    assert metadata["target"] == "label"
    assert metadata["primary_model"] == "random_forest"
    assert metadata["primary_model_display_name"] == "Random Forest"
    assert metadata["decision_threshold"] == 0.55
    assert metadata["model_thresholds"]["random_forest"] == 0.55
    assert metadata["model_thresholds"]["logistic_regression"] == 0.55
    assert metadata["excluded_columns"] == ["id", "attack_cat"]
    assert metadata["primary_model_path"] == "models/random_forest_model.pkl"
    assert len(metadata["numeric_features"]) == 39
    assert metadata["categorical_features"] == ["proto", "service", "state"]
    assert set(feature_columns) == set(PredictionRequest.model_fields)


def test_openapi_schema_documents_core_endpoints() -> None:
    openapi_schema = app.openapi()
    paths = openapi_schema["paths"]

    assert openapi_schema["info"]["title"] == "Network Intrusion Detection System"
    assert "/health" in paths
    assert "/predict" in paths
    assert "/metrics" in paths
    assert paths["/health"]["get"]["responses"]["200"]
    assert paths["/predict"]["post"]["requestBody"]["required"] is True
    assert paths["/predict"]["post"]["responses"]["200"]
    assert paths["/metrics"]["get"]["responses"]["200"]


def test_readme_contains_required_dataset_citation() -> None:
    readme = README_PATH.read_text(encoding="utf-8")

    assert "## Dataset Citation" in readme
    assert "https://research.unsw.edu.au/projects/unsw-nb15-dataset" in readme
    assert "Moustafa" in readme
    assert "Slay" in readme
    assert "Sarhan" in readme
    assert (
        "NetFlow Datasets for Machine Learning-Based Network Intrusion Detection Systems"
        in readme
    )


def test_dependency_files_separate_runtime_and_development_tools() -> None:
    runtime_requirements = RUNTIME_REQUIREMENTS_PATH.read_text(encoding="utf-8")
    dev_requirements = DEV_REQUIREMENTS_PATH.read_text(encoding="utf-8")

    assert "-r requirements.txt" in dev_requirements
    assert "pytest" in dev_requirements
    assert "httpx" in dev_requirements
    assert "ruff" in dev_requirements
    assert "pytest" not in runtime_requirements
    assert "httpx" not in runtime_requirements
    assert "ruff" not in runtime_requirements
