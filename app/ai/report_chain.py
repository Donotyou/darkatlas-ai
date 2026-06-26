from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from ..models import Asset
from ..config import settings
from datetime import datetime, timezone
import json

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

prompt = ChatPromptTemplate.from_template("""
You are a cybersecurity analyst writing an asset inventory report.
Write a clear, professional security report based ONLY on the assets below.
Do NOT invent any data.

Assets ({count} total):
{assets}

Today: {today}

Write a markdown report with:
1. Executive Summary
2. Asset Breakdown by Type
3. Risk Highlights
4. Recommendations
""")

def run(filters: dict, db: Session):
    query = db.query(Asset)
    if filters.get("type"):
        query = query.filter(Asset.type == filters["type"])
    if filters.get("status"):
        query = query.filter(Asset.status == filters["status"])

    assets = query.limit(100).all()
    if not assets:
        return {"error": "No assets found"}

    assets_data = [
        {"id": a.id, "type": a.type, "value": a.value,
         "status": a.status, "tags": a.tags, "metadata": a.metadata_}
        for a in assets
    ]

    chain = prompt | llm
    response = chain.invoke({
        "assets": json.dumps(assets_data, indent=2),
        "count": len(assets_data),
        "today": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    })

    return {
        "report": response.content,
        "asset_count": len(assets_data),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }