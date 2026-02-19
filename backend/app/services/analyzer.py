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
from pathlib import Path
import json


# ✅ DRUG-LEVEL CLINICAL INTERPRETATION ENGINE ⭐⭐⭐⭐⭐
def generate_drug_interpretation(drug, risk_label, gene, phenotype):
    if not gene:
        return "No pharmacogenomic gene associations detected for this medication."

    base = f"{drug} response influenced by {gene} ({phenotype} phenotype). "

    if risk_label == "Safe":
        return base + "Genetic findings do not suggest elevated pharmacogenomic risk. Standard therapy appropriate."

    if risk_label == "Adjust Dosage":
        return base + "Genetic variation may alter drug metabolism or response. Clinical monitoring or dose adjustment recommended."

    if risk_label == "Toxic":
        return base + "Genetic profile indicates elevated toxicity risk. Alternative therapy or major dose modification advised."

    if risk_label == "Ineffective":
        return base + "Genetic variation may reduce therapeutic efficacy. Consider alternative medication."

    return base + "Pharmacogenomic impact uncertain."


def run_analysis_from_path(vcf_path: str, drug: str, patient_id: str):

    try:
        # ✅ 1) Parse VCF
        variants = parse_vcf(vcf_path)

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
        diplotype_consistent = True  # ⭐ NEW

        if primary_gene and primary_gene in pgx_profile:

            gene_block = pgx_profile[primary_gene]

            phenotype = gene_block.get("phenotype")
            diplotype = gene_block.get("diplotype")

            activity_score = gene_block.get("activity_score")
            decision_trace = gene_block.get("decision_trace")

            # ---------- COLLECT DETECTED VARIANTS ----------
            detected_variants = [
                v for v in variants
                if v.get("gene") == primary_gene
            ]

            # ---------- STAR AUTO-FILL BEFORE CONSISTENCY CHECK ----------
            # Robustly support rsid_star_map entries that are either dicts or simple strings.
            BASE = Path(__file__).resolve().parents[1]
            try:
                rsid_star_map = json.loads((BASE / "rules" / "rsid_star_map.json").read_text())

            except Exception:
                rsid_star_map = {}

            for v in detected_variants:
                if not v.get("star") and v.get("rsid") in rsid_star_map:
                    mapping = rsid_star_map[v["rsid"]]

                    # support both formats: {"allele":"*3", "gene":"CYP2C9"}  OR  "*3"
                    if isinstance(mapping, dict):
                        allele = mapping.get("allele") or mapping.get("allele_name") or mapping.get("value")
                    else:
                        allele = mapping  # string case

                    if allele:
                        v["star"] = allele

            # ---------- DIPLOTYPE CONSISTENCY CHECK ----------
            if diplotype:
                exp_counts = {}
                try:
                    left, right = diplotype.split("/")
                    exp_counts[left] = exp_counts.get(left, 0) + 1
                    exp_counts[right] = exp_counts.get(right, 0) + 1
                except Exception:
                    exp_counts = {}

                obs_counts = {}
                for v in detected_variants:
                    star = v.get("star")
                    if star:
                        obs_counts[star] = obs_counts.get(star, 0) + (
                            v.get("alt_count", 1)
                            if isinstance(v.get("alt_count"), int)
                            else 1
                        )

                # Compare expected vs observed counts
                for allele, exp_ct in exp_counts.items():
                    if obs_counts.get(allele, 0) < exp_ct:
                        diplotype_consistent = False
                        break

        # ✅ 4) Recommendation
        rec = get_clinical_recommendation(drug, primary_gene, phenotype)

        # ✅ 5) LLM Explanation
        if not detected_variants or not phenotype:
            llm = {
                "summary": rec.get("text"),
                "mechanism": "No variant-level evidence available.",
                "evidence": "None",
                "citations": [],
                "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
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

        timestamp = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

        drug_interpretation = generate_drug_interpretation(
            drug.upper(),
            risk_block["risk_assessment"]["risk_label"],
            primary_gene,
            phenotype
        )

        final = {
            "patient_id": patient_id,
            "drug": drug.upper(),
            "timestamp": timestamp,
            "risk_assessment": risk_block["risk_assessment"],
            "pharmacogenomic_profile": {
                "primary_gene": primary_gene,
                "diplotype": diplotype,
                "phenotype": phenotype,
                "activity_score": activity_score,
                "decision_trace": decision_trace,
                "detected_variants": detected_variants
            },
            "drug_level_interpretation": drug_interpretation,
            "clinical_recommendation": rec,
            "llm_generated_explanation": llm,
            "quality_metrics": {
                "vcf_parsing_success": True,
                "variant_count": len(variants),
                "gene_match_success": True if primary_gene else False,
                "llm_success": True,
                "diplotype_consistency_check": diplotype_consistent  # ⭐ NEW
            }
        }

        # ✅ Schema validation
        try:
            FinalOutput.parse_obj(final)
        except ValidationError as e:
            logging.error(f"Schema validation failed: {e}")
            raise HTTPException(status_code=500, detail="Internal schema validation failure")

        return jsonable_encoder(final)

    except Exception as e:
        logging.exception("Analysis pipeline failure")
        raise HTTPException(status_code=500, detail=f"Analysis engine failure: {str(e)}")
