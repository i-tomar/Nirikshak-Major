"""
NIRIKSHAK AI — Model Evaluation & Explainability Router
Serves metrics, feature importance rankings, and confusion matrices for the ML evaluation dashboard.
"""

import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class ModelFeatureImportance(BaseModel):
    name: str
    importance: float
    rank: int


class ModelFeaturesResponse(BaseModel):
    features: list[ModelFeatureImportance]


class ModelMetricsResponse(BaseModel):
    model_name: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    f1: float
    roc_auc: float
    train_samples: int
    test_samples: int
    total_samples: int
    evaluated_at: str
    evaluation_methodology: str
    class_distribution: dict[str, int]
    confusion_matrix: list[list[int]]
    confusion_matrix_labels: list[str]


class PendingEvaluation(BaseModel):
    status: Literal["not_evaluated"] = "not_evaluated"


@router.get("/metrics", response_model=ModelMetricsResponse | PendingEvaluation)
def get_model_metrics() -> ModelMetricsResponse | PendingEvaluation:
    report = DATA_DIR / "analysis" / "evaluation_report.json"
    if not report.is_file():
        return PendingEvaluation()
    return ModelMetricsResponse.model_validate_json(report.read_bytes())


@router.get("/features", response_model=ModelFeaturesResponse)
def get_model_features() -> ModelFeaturesResponse:
    card = MODELS_DIR / "model_card.json"
    if not card.is_file():
        return ModelFeaturesResponse(features=[])
    data = json.loads(card.read_bytes())
    return ModelFeaturesResponse(features=data.get("feature_importances", []))
