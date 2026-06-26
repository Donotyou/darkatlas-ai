from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import QueryRequest, RiskRequest, EnrichRequest, ReportRequest
from ..ai import query_chain, risk_chain, enrich_chain, report_chain

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("/query")
def query_assets(body: QueryRequest, db: Session = Depends(get_db)):
    return query_chain.run(body.question, db)

@router.post("/risk")
def assess_risk(body: RiskRequest, db: Session = Depends(get_db)):
    return risk_chain.run(body.asset_ids, db)

@router.post("/enrich")
def enrich_asset(body: EnrichRequest, db: Session = Depends(get_db)):
    return enrich_chain.run(body.asset_id, db)

@router.post("/report")
def generate_report(body: ReportRequest, db: Session = Depends(get_db)):
    return report_chain.run(body.filters, db)