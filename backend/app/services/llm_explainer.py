import os
import json

from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_explanation(
    patient_id,
    drug,
    primary_gene,
    phenotype,
    detected_variants,
    recommendation_text
):
    """
    LLM-based clinical explanation generator
    """

    variant_text = ", ".join(
        [v.get("rsid", "unknown") for v in detected_variants]
    )

    prompt = f"""
Return ONLY JSON with keys:
summary, mechanism, evidence, citations

Drug: {drug}
Gene: {primary_gene}
Phenotype: {phenotype}
Variants: {variant_text}
Recommendation: {recommendation_text}

Citations must reference CPIC or PharmGKB.
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
        )

        text = completion.choices[0].message.content.strip()

        # ✅ Robust JSON cleaning (VERY IMPORTANT)
        if text.startswith("```"):
            text = text.split("```")[1].strip()

        payload = json.loads(text)

        # ✅ Safety validation (LLMs sometimes omit fields)
        payload.setdefault("summary", recommendation_text)
        payload.setdefault("mechanism", "Variant impacts gene function.")
        payload.setdefault("evidence", "CPIC")
        payload.setdefault("citations", ["CPIC guideline"])

    except Exception:

        # ✅ Failure-proof fallback
        payload = {
            "summary": recommendation_text,
            "mechanism": "Variant impacts gene function.",
            "evidence": "CPIC",
            "citations": ["CPIC guideline"]
        }

    payload["generated_at"] = datetime.utcnow() \
        .replace(microsecond=0) \
        .isoformat() + "Z"

    return payload
