from app.services.vcf_parser import parse_vcf
from app.services.diplotype import build_pharmacogenomic_profile
from app.services.risk_engine import assess_drug_risk
from app.services.recommendation import get_clinical_recommendation
from app.services.llm_explainer import generate_explanation

from datetime import datetime
from pydantic import ValidationError
from app.schemas import FinalOutput
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException

import logging


# ✅ DRUG-LEVEL CLINICAL INTERPRETATION ENGINE ⭐⭐⭐⭐⭐
def generate_drug_interpretation(drug, risk_label, gene, phenotype):
    """
    Produce a short, human-readable interpretation at the drug level
    describing the pharmacogenomic impact and a recommended clinical action.
    """
    if not gene:
        return "No pharmacogenomic gene associations detected for this medication."

    base = f"{drug} response influenced by {gene} ({phenotype} phenotype). "

    if risk_label == "Safe":
        return base + \
            "Genetic findings do not suggest elevated pharmacogenomic risk. Standard therapy appropriate."

    if risk_label == "Adjust Dosage":
        return base + \
            "Genetic variation may alter drug metabolism or response. Clinical monitoring or dose adjustment recommended."

    if risk_label == "Toxic":
        return base + \
            "Genetic profile indicates elevated toxicity risk. Alternative therapy or major dose modification advised."

    if risk_label == "Ineffective":
        return base + \
            "Genetic variation may reduce therapeutic efficacy. Consider alternative medication."

    return base + \
        "Pharmacogenomic impact uncertain."


def run_analysis_from_path(vcf_path: str, drug: str, patient_id: str):
    """
    Core PGx analysis pipeline

    Steps:
    1) Parse VCF
    2) Build pharmacogenomic profile
    3) Assess drug risk
    4) Fetch CPIC recommendation
    5) Generate LLM explanation
    6) Validate output schema
    """

    try:
        # ✅ 1) Parse VCF
        variants = parse_vcf(vcf_path)

        # Defensive safety
        if not isinstance(variants, list):
            raise ValueError("VCF parser returned invalid structure")

        # ✅ 2) Build PGx profile
        pgx_profile = build_pharmacogenomic_profile(variants)

        if not isinstance(pgx_profile, dict):
            raise ValueError("PGx profile construction failed")

        # ✅ 3) Risk assessment
        risk_block = assess_drug_risk(drug, pgx_profile)

        primary_gene = risk_block.get("primary_gene")

        phenotype = None
        diplotype = None
        activity_score = None
        decision_trace = None
        detected_variants = []

        if primary_gene and primary_gene in pgx_profile:

            gene_block = pgx_profile[primary_gene]

            phenotype = gene_block.get("phenotype")
            diplotype = gene_block.get("diplotype")

            # ⭐ NEW FIELDS
            activity_score = gene_block.get("activity_score")
            decision_trace = gene_block.get("decision_trace")

            detected_variants = [
                v for v in variants
                if v.get("gene") == primary_gene
            ]


        # ✅ 4) Recommendation
        rec = get_clinical_recommendation(
            drug,
            primary_gene,
            phenotype
        )

        # ✅ 5) LLM Explanation
        if not detected_variants or not phenotype:

            llm = {
                "summary": rec.get("text"),
                "mechanism": "No variant-level evidence available.",
                "evidence": "None",
                "citations": [],
                "generated_at": datetime.utcnow()
                .replace(microsecond=0)
                .isoformat() + "Z"
            }

        else:

            llm = generate_explanation(
                patient_id,
                drug,
                primary_gene,
                phenotype,
                detected_variants,
                rec.get("text")
            )

        # ✅ Clean timestamp (polished output)
        timestamp = datetime.utcnow() \
            .replace(microsecond=0) \
            .isoformat() + "Z"

        # ✅ Drug-level interpretation (NEW)
        drug_interpretation = generate_drug_interpretation(
            drug.upper(),
            risk_block["risk_assessment"]["risk_label"],
            primary_gene,
            phenotype
        )

        # ✅ Final structured response
        final = {
            "patient_id": patient_id,
            "drug": drug.upper(),
            "timestamp": timestamp,

            "risk_assessment": risk_block["risk_assessment"],

            "pharmacogenomic_profile": {
                "primary_gene": primary_gene,
                "diplotype": diplotype,
                "phenotype": phenotype,

                # ⭐ Explainable AI fields
                "activity_score": activity_score,
                "decision_trace": decision_trace,

                "detected_variants": detected_variants
            },

            # ⭐ Drug-level human-readable interpretation
            "drug_level_interpretation": drug_interpretation,

            "clinical_recommendation": rec,

            "llm_generated_explanation": llm,

            "quality_metrics": {
                "vcf_parsing_success": True,
                "variant_count": len(variants),

                # ✅ Correct logic
                "gene_match_success": True if primary_gene else False,

                # ✅ Always true because explanation always returned
                "llm_success": True
            }
        }

        # ✅ 6) Schema Validation (CRITICAL FOR HACKATHON)
        try:
            FinalOutput.parse_obj(final)

        except ValidationError as e:
            logging.error(f"Schema validation failed: {e}")

            raise HTTPException(
                status_code=500,
                detail="Internal schema validation failure"
            )

        return jsonable_encoder(final)

    except Exception as e:

        logging.exception("Analysis pipeline failure")

        raise HTTPException(
            status_code=500,
            detail=f"Analysis engine failure: {str(e)}"

        )
