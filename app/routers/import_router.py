from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from ..database import get_db
from ..models import Asset, AssetRelationship

router = APIRouter(prefix="/import", tags=["Import"])

@router.post("/")
def import_assets(body: dict, db: Session = Depends(get_db)):
    assets = body.get("assets", [])
    results = {"imported": 0, "updated": 0, "failed": 0, "errors": []}

    for raw in assets:
        try:
            if not raw.get("type") or not raw.get("value"):
                raise ValueError("Missing type or value")

            now = datetime.now(timezone.utc)

            existing = db.query(Asset).filter(
                Asset.type == raw["type"],
                Asset.value == raw["value"]
            ).first()

            if existing:
                existing.last_seen = now
                existing.status = "active"
                existing.tags = list(set((existing.tags or []) + (raw.get("tags") or [])))
                existing.metadata_ = {**(existing.metadata_ or {}), **(raw.get("metadata") or {})}
                results["updated"] += 1
            else:
                asset = Asset(
                    id        = raw.get("id") or str(__import__("uuid").uuid4()),
                    type      = raw["type"],
                    value     = raw["value"],
                    status    = raw.get("status", "active"),
                    source    = raw.get("source", "import"),
                    tags      = raw.get("tags", []),
                    metadata_ = raw.get("metadata", {}),
                    first_seen = now,
                    last_seen  = now,
                )
                db.add(asset)
                results["imported"] += 1

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({"record": raw, "error": str(e)})

    db.commit()
    return results