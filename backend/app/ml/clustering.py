"""Infer behavioral similarity from measured wallet features."""

from pathlib import Path

import numpy as np
import polars as pl
from app.ml.features import NUMERICAL_FEATURE_NAMES
from app.schemas.clustering import (
    ClusteringDiagnostics,
    ClusterProfile,
    ClusterProfilesResponse,
    SimilarWallet,
    SimilarWalletsResponse,
    WalletClusterDetailResponse,
)
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from threadpoolctl import threadpool_limits

BASE = Path(__file__).resolve().parents[2] / "data" / "analysis"
EXCLUDED_FEATURE_NAMES = {"wallet_degree", "amount_fragmentation_score"}
CLUSTER_FEATURE_NAMES = [
    f for f in NUMERICAL_FEATURE_NAMES if f not in EXCLUDED_FEATURE_NAMES
]


def prepare_clustering_matrix(
    features: pl.DataFrame,
) -> tuple[list[str], np.ndarray, list[str]]:
    names = CLUSTER_FEATURE_NAMES
    matrix = features.select(names).to_numpy().astype(float)
    if not np.isfinite(matrix).all():
        raise ValueError("Non-finite clustering feature")
    for i, name in enumerate(names):
        if name == "input_output_ratio":
            matrix[:, i] = np.clip(np.log10(np.maximum(matrix[:, i], 1e-8)), -3, 3)
        elif name not in {"burstiness", "night_activity_ratio"}:
            matrix[:, i] = np.log1p(matrix[:, i])
    return features["wallet_address"].to_list(), matrix, names


def run_behavioral_clustering(
    features: pl.DataFrame, random_state: int = 42, leads: pl.DataFrame | None = None
) -> tuple[ClusterProfilesResponse, pl.DataFrame]:
    """Fit up to six groups and measure separation on a deterministic sample."""
    addresses, matrix, names = prepare_clustering_matrix(features)
    k = min(6, len(np.unique(matrix, axis=0)))
    if not k:
        raise ValueError("No wallets available for clustering")
    with threadpool_limits(limits=1):
        model = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(matrix)
        labels = model.labels_
        distances = np.linalg.norm(matrix - model.cluster_centers_[labels], axis=1)
        coords = np.zeros((len(matrix), 2))
        if len(matrix) > 1:
            coords[:] = PCA(n_components=2, svd_solver="full").fit_transform(matrix)
        silhouette = None
        if 1 < k < len(matrix):
            silhouette = float(
                silhouette_score(
                    matrix,
                    labels,
                    sample_size=min(len(matrix), 2000),
                    random_state=random_state,
                )
            )
    profiles = []
    for group, center in enumerate(model.cluster_centers_):
        mask = labels == group
        changes = (center - matrix.mean(axis=0)) / np.maximum(matrix.std(axis=0), 1e-9)
        traits = [names[i] for i in np.argsort(-np.abs(changes), kind="stable")[:3]]
        members = features.filter(pl.Series(mask))
        measurements = (
            leads
            if leads is not None
            else pl.read_parquet(BASE / "investigative_leads.parquet")
        )
        matched = measurements.join(
            members.select("wallet_address"), on="wallet_address", how="semi"
        )
        profiles.append(
            ClusterProfile(
                cluster_id=group,
                label=f"Behavioral group {group + 1}",
                description=f"Inferred group differentiated by {', '.join(traits)}.",
                wallet_count=len(members),
                average_risk_score=matched["risk_score"].mean(),
                anomaly_rate=matched["is_outlier"].mean(),
                centroid_distance_mean=distances[mask].mean(),
                centroid_distance_median=np.median(distances[mask]),
                top_differentiating_features=traits,
                centroid_summary=dict(zip(names, center.tolist(), strict=True)),
            )
        )
    assignments = pl.DataFrame(
        {
            "wallet_address": addresses,
            "cluster_id": labels,
            "cluster_label": [profiles[i].label for i in labels],
            "distance_to_centroid": distances,
            "pca_x": coords[:, 0],
            "pca_y": coords[:, 1],
        }
    )
    return ClusterProfilesResponse(
        total_clusters=k,
        total_wallets=len(matrix),
        clustering_algorithm="KMeans",
        clusters=profiles,
        diagnostics=ClusteringDiagnostics(
            k_values=[k],
            inertias={str(k): model.inertia_},
            selected_k=k,
            silhouette_scores={str(k): silhouette} if silhouette is not None else {},
            selected_k_silhouette=silhouette,
        ),
    ), assignments


def load_cluster_assignments() -> pl.DataFrame:
    return pl.read_parquet(BASE / "wallet_clusters.parquet")


def load_cluster_profiles() -> ClusterProfilesResponse:
    return ClusterProfilesResponse.model_validate_json(
        (BASE / "cluster_profiles.json").read_bytes()
    )


def get_wallet_cluster(wallet: str) -> WalletClusterDetailResponse | None:
    rows = load_cluster_assignments().filter(pl.col("wallet_address") == wallet)
    if rows.is_empty():
        return None
    row = rows.row(0, named=True)
    profile = load_cluster_profiles().clusters[row["cluster_id"]]
    return WalletClusterDetailResponse(**row, cluster_profile=profile)


def find_similar_wallets(wallet: str, top_n: int = 5) -> SimilarWalletsResponse:
    target = get_wallet_cluster(wallet)
    if target is None:
        raise KeyError(wallet)
    addresses, matrix, names = prepare_clustering_matrix(
        pl.read_parquet(BASE / "wallet_features.parquet")
    )
    delta = np.abs(matrix - matrix[addresses.index(wallet)])
    distances = np.linalg.norm(delta, axis=1)
    order = np.lexsort((addresses, distances))
    assignments = {
        r["wallet_address"]: r for r in load_cluster_assignments().iter_rows(named=True)
    }
    candidates = [i for i in order if addresses[i] != wallet][:top_n]
    results = []
    for i in candidates:
        similarity = 1.0 / (1.0 + distances[i])
        results.append(
            SimilarWallet(
                **assignments[addresses[i]],
                similarity_score=similarity,
                similarity_percent=100 * similarity,
                shared_behavioral_traits=[
                    names[j] for j in np.argsort(delta[i], kind="stable")[:3]
                ],
            )
        )
    return SimilarWalletsResponse(
        target_wallet=wallet,
        target_cluster_id=target.cluster_id,
        target_cluster_label=target.cluster_label,
        total_candidates=len(matrix) - 1,
        returned_count=len(results),
        similar_wallets=results,
    )
