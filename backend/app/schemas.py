from pydantic import BaseModel
from typing import List, Optional

class DetectedVariant(BaseModel):
    gene: Optional[str]
    rsid: Optional[str]
    genotype: Optional[str]
    star: Optional[str]
    info: Optional[dict]

class RiskAssessment(BaseModel):
    risk_label: str
    confidence_score: float
    severity: str

class LLMExplanation(BaseModel):
    summary: str
    mechanism: Optional[str] = None
    evidence: Optional[str] = None
    citations: Optional[List[str]] = None
    generated_at: str

class PharmacogenomicProfile(BaseModel):
    primary_gene: Optional[str]
    diplotype: Optional[str]
    phenotype: Optional[str]
    activity_score: Optional[float] = None
    decision_trace: Optional[dict] = None
    detected_variants: List[DetectedVariant]


class FinalOutput(BaseModel):
    patient_id: str
    drug: str
    timestamp: str
    risk_assessment: RiskAssessment
    pharmacogenomic_profile: PharmacogenomicProfile
    clinical_recommendation: dict
    llm_generated_explanation: LLMExplanation
    quality_metrics: dict


from typing import List, Optional


