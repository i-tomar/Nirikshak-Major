"""Rank investigative leads using empirical percentiles."""

from dataclasses import dataclass

import numpy as np
import polars as pl
from scipy.stats import rankdata


@dataclass(frozen=True)
class RiskWeights:
    anomaly: float = 0.55
    activity: float = 0.20
    network: float = 0.10
    behavior: float = 0.15


@dataclass(frozen=True)
class RiskThresholds:
    critical: float = 90
    high: float = 75
    medium: float = 50


def rank_leads(features: pl.DataFrame, anomalies: pl.DataFrame) -> pl.DataFrame:
    """Calculate relative priorities, with wallet address as the final tie breaker."""
    rows = features.join(anomalies, on="wallet_address")
    weights = RiskWeights()
    thresholds = RiskThresholds()
    signals = {
        "activity": "transaction_count",
        "network": "unique_ip_count",
        "behavior": "amount_fragmentation_score",
    }
    scores = {"anomaly": rows["anomaly_percentile"].to_numpy()}
    for group, feature in signals.items():
        scores[group] = 100 * (rankdata(rows[feature]) - 0.5) / len(rows)
    priority = sum(scores[group] * getattr(weights, group) for group in scores)
    tiers = np.select(
        [
            priority >= thresholds.critical,
            priority >= thresholds.high,
            priority >= thresholds.medium,
        ],
        ["CRITICAL", "HIGH", "MEDIUM"],
        default="LOW",
    )
    return rows.with_columns(
        pl.Series("risk_score", np.round(priority, 2)),
        pl.Series("risk_level", tiers),
        *[pl.Series(f"sub_{group}_score", values) for group, values in scores.items()],
    ).sort(
        ["risk_score", "anomaly_score", "wallet_address"],
        descending=[True, True, False],
    )
