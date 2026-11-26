"""Seeded Isolation Forest with safe reconstruction from numeric training inputs."""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import numpy as np
import polars as pl
from app.ml.features import NUMERICAL_FEATURE_NAMES
from scipy.stats import rankdata
from sklearn.ensemble import IsolationForest

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"


@dataclass(frozen=True)
class IsolationForestConfig:
    random_state: int = 42
    n_estimators: int = 100
    contamination: float = 0.05


class AnomalyModel:
    def __init__(self, config: IsolationForestConfig = IsolationForestConfig()) -> None:
        self.config = config
        self.model = IsolationForest(**asdict(config), n_jobs=1)
        self.trained_at = ""
        self.dataset_size = 0

    def fit_score(
        self, features: pl.DataFrame, output: Path = MODEL_DIR
    ) -> pl.DataFrame:
        """Fit on ordered rows and persist only data and parameters needed to refit."""
        matrix = features.select(NUMERICAL_FEATURE_NAMES).to_numpy()
        self.model.fit(matrix)
        raw = -self.model.score_samples(matrix)
        self.dataset_size = len(matrix)
        self.trained_at = datetime.now(UTC).isoformat()
        output.mkdir(parents=True, exist_ok=True)
        artifact = output / "isolation_training.parquet"
        features.select(NUMERICAL_FEATURE_NAMES).write_parquet(artifact)
        metadata = {
            "dataset_size": len(matrix),
            "trained_at": self.trained_at,
            "config": asdict(self.config),
            "features": NUMERICAL_FEATURE_NAMES,
            "sha256": sha256(artifact.read_bytes()).hexdigest(),
        }
        (output / "model_card.json").write_text(json.dumps(metadata), encoding="utf-8")
        span = float(np.ptp(raw))
        scores = np.round((raw - raw.min()) / span, 4) if span else np.zeros_like(raw)
        return features.select("wallet_address").with_columns(
            pl.Series("anomaly_score", scores),
            pl.Series(
                "anomaly_percentile",
                np.round(100 * (rankdata(raw) - 0.5) / len(raw), 2),
            ),
            pl.Series("is_outlier", self.model.predict(matrix) == -1),
        )

    @classmethod
    def load(cls, directory: Path = MODEL_DIR) -> "AnomalyModel":
        """Rebuild from hash-checked numeric inputs using the saved seed."""
        card = json.loads((directory / "model_card.json").read_text(encoding="utf-8"))
        artifact = directory / "isolation_training.parquet"
        if sha256(artifact.read_bytes()).hexdigest() != card["sha256"]:
            raise ValueError("Training input hash mismatch")
        matrix = pl.read_parquet(artifact).select(NUMERICAL_FEATURE_NAMES).to_numpy()
        if matrix.shape != (card["dataset_size"], len(NUMERICAL_FEATURE_NAMES)):
            raise ValueError("Training input shape mismatch")
        result = cls(IsolationForestConfig(**card["config"]))
        result.model.fit(matrix)
        result.trained_at = card["trained_at"]
        result.dataset_size = len(matrix)
        return result
