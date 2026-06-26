from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssetOut(BaseModel):
    id: str
    type: str
    value: str
    status: str
    first_seen: datetime
    last_seen: datetime
    source: str
    tags: list
    metadata: dict = {}

    class Config:
        from_attributes = True

class ImportRequest(BaseModel):
    assets: list[dict]

class QueryRequest(BaseModel):
    question: str

class RiskRequest(BaseModel):
    asset_ids: list[str]

class EnrichRequest(BaseModel):
    asset_id: str

class ReportRequest(BaseModel):
    filters: Optional[dict] = {}