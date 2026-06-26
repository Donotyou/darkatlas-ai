from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from ..models import Asset
from ..config import settings
from datetime import datetime, timezone
import json

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

prompt = ChatPromptTemplate.from_template("""
You are a cybersecurity risk analyst.
Analyze ONLY the following assets and return a risk assessment.
Do NOT invent assets that are not listed below.

Assets:
{assets}

Today: {today}

Respond ONLY with valid JSON:
{{
  "risk_score": <0-100>,
  "risk_level": "<low|medium|high|critical>",
  "findings": ["finding1", "finding2"],
  "summary": "<2-3 sentences>"
}}
""")

def run(asset_ids: list, db: Session):
    assets = db.query(Asset).filter(Asset.id.in_(asset_ids)).all()
    if not assets:
        return {"error": "No assets found with provided IDs"}

    assets_data = [
        {"id": a.id, "type": a.type, "value": a.value,
         "status": a.status, "tags": a.tags, "metadata": a.metadata_}
        for a in assets
    ]

    chain = prompt | llm
    response = chain.invoke({
        "assets": json.dumps(assets_data, indent=2),
        "today": datetime.now(timezone.utc).strftime("%Y-%m-%d")
    })

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {"error": f"Parse error: {str(e)}", "raw": response.content}