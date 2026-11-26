"""Public schemas for inferred behavioral similarity."""

from pydantic import BaseModel


class ClusterProfile(BaseModel):
    cluster_id: int
    label: str
    description: str
    wallet_count: int
    average_risk_score: float
    anomaly_rate: float
    centroid_distance_mean: float
    centroid_distance_median: float
    top_differentiating_features: list[str]
    centroid_summary: dict[str, float]


class ClusteringDiagnostics(BaseModel):
    k_values: list[int]
    inertias: dict[str, float]
    silhouette_scores: dict[str, float]
    selected_k: int
    selected_k_silhouette: float | None


class ClusterProfilesResponse(BaseModel):
    total_clusters: int
    total_wallets: int
    clustering_algorithm: str
    diagnostics: ClusteringDiagnostics
    clusters: list[ClusterProfile]


class WalletClusterAssignment(BaseModel):
    wallet_address: str
    cluster_id: int
    cluster_label: str
    distance_to_centroid: float
    pca_x: float
    pca_y: float


class ClusterDetailResponse(BaseModel):
    cluster: ClusterProfile
    total_wallets: int
    returned_count: int
    offset: int
    limit: int
    wallets: list[WalletClusterAssignment]


class WalletClusterDetailResponse(WalletClusterAssignment):
    cluster_profile: ClusterProfile


class SimilarWallet(WalletClusterAssignment):
    similarity_score: float
    similarity_percent: float
    shared_behavioral_traits: list[str]


class SimilarWalletsResponse(BaseModel):
    target_wallet: str
    target_cluster_id: int
    target_cluster_label: str
    total_candidates: int
    returned_count: int
    similar_wallets: list[SimilarWallet]
