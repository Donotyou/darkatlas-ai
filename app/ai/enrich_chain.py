from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from ..models import Asset
from ..config import settings
import json

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

prompt = ChatPromptTemplate.from_template("""
You are a cybersecurity asset classifier.
Analyze this asset and classify it.

Asset:
{asset}

Respond ONLY with valid JSON:
{{
  "environment": "<production|staging|development|unknown>",
  "category": "<string>",
  "criticality": "<low|medium|high|critical>",
  "suggested_tags": ["tag1", "tag2"],
  "notes": "<one sentence>"
}}
""")

def run(asset_id: str, db: Session):
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return {"error": "Asset not found"}

    asset_data = {
        "id": asset.id, "type": asset.type, "value": asset.value,
        "status": asset.status, "tags": asset.tags, "metadata": asset.metadata_
    }

    chain = prompt | llm
    response = chain.invoke({"asset": json.dumps(asset_data, indent=2)})

    try:
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        enrichment = json.loads(raw.strip())

        
        new_tags = list(set((asset.tags or []) + enrichment.get("suggested_tags", [])))
        asset.tags = new_tags
        db.commit()

        return {"asset_id": asset_id, "enrichment": enrichment}
    except Exception as e:
        return {"error": f"Parse error: {str(e)}", "raw": response.content}