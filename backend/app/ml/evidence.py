"""Measurements shown in the alert and investigation endpoints."""

from pydantic import BaseModel


class EvidenceReason(BaseModel):
    category: str
    feature: str
    value: float
    baseline: float
    explanation: str
