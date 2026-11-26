"""Read-only behavioral clustering endpoints."""

import re

import polars as pl
from app.ml import clustering
from app.schemas.clustering import (
    ClusterDetailResponse,
    ClusterProfilesResponse,
    SimilarWalletsResponse,
    WalletClusterAssignment,
    WalletClusterDetailResponse,
)
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


def wallet_address(value: str) -> str:
    address = value.removeprefix("wallet:")
    if not re.fullmatch(r"[A-Za-z0-9]{5,128}", address):
        raise HTTPException(400, "Invalid wallet identifier")
    return address


@router.get("", response_model=ClusterProfilesResponse)
def profiles() -> ClusterProfilesResponse:
    try:
        return clustering.load_cluster_profiles()
    except FileNotFoundError as exc:
        raise HTTPException(404, "Cluster analysis not found") from exc


@router.get("/wallet/{wallet}", response_model=WalletClusterDetailResponse)
def wallet_detail(wallet: str) -> WalletClusterDetailResponse:
    address = wallet_address(wallet)
    profiles()
    result = clustering.get_wallet_cluster(address)
    if result is None:
        raise HTTPException(404, "Wallet not found")
    return result


@router.get("/similar/{wallet}", response_model=SimilarWalletsResponse)
def similar(wallet: str, top_n: int = Query(5, ge=1, le=50)) -> SimilarWalletsResponse:
    address = wallet_address(wallet)
    profiles()
    try:
        return clustering.find_similar_wallets(address, top_n)
    except KeyError as exc:
        raise HTTPException(404, "Wallet not found") from exc


@router.get("/{cluster_id}", response_model=ClusterDetailResponse)
def detail(
    cluster_id: int,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sort_by: str = "distance",
) -> ClusterDetailResponse:
    groups = profiles().clusters
    if not 0 <= cluster_id < len(groups):
        raise HTTPException(404, "Cluster not found")
    order = {"distance": "distance_to_centroid", "address": "wallet_address"}.get(
        sort_by
    )
    if order is None:
        raise HTTPException(400, "Invalid sort_by")
    members = clustering.load_cluster_assignments().filter(
        pl.col("cluster_id") == cluster_id
    )
    page = members.sort(order).slice(offset, limit).to_dicts()
    return ClusterDetailResponse(
        cluster=groups[cluster_id],
        total_wallets=len(members),
        returned_count=len(page),
        offset=offset,
        limit=limit,
        wallets=[WalletClusterAssignment.model_validate(row) for row in page],
    )
