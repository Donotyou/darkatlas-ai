from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from ..models import Asset
from ..config import settings
import json

llm = ChatGroq(model="llama-3.1-8b-instant", api_key=settings.GROQ_API_KEY)

prompt = ChatPromptTemplate.from_template("""
You are a cybersecurity analyst assistant.
A user asked: "{question}"

Here are ALL the assets in the system:
{assets}

Based on the user's question, return ONLY the assets that match.
Think carefully about what the user is asking — look at type, status, tags, metadata (like expires dates), and values.
Do NOT invent assets. Only return assets from the list above.

Respond ONLY with valid JSON:
{{
  "reasoning": "<one sentence explaining what you looked for>",
  "count": <number>,
  "assets": [
    {{"id": "...", "type": "...", "value": "...", "status": "...", "tags": [...], "metadata": {{...}}}}
  ]
}}
""")

def run(question: str, db: Session):
    if not question or len(question.strip()) < 3:
        return {"error": "Question is too short or empty"}

    # جيبي كل الداتا من الداتابيز
    all_assets = db.query(Asset).all()
    if not all_assets:
        return {"error": "No assets found in database"}

    assets_data = [
        {
            "id": a.id,
            "type": a.type,
            "value": a.value,
            "status": a.status,
            "tags": a.tags,
            "metadata": a.metadata_
        }
        for a in all_assets
    ]

    chain = prompt | llm
    response = chain.invoke({
        "question": question,
        "assets": json.dumps(assets_data, indent=2)
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