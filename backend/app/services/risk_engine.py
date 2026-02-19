import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RULES_DIR = BASE / "rules"

_risk_rules = json.loads((RULES_DIR / "risk_rules.json").read_text())

def assess_drug_risk(drug_name, pgx_profile):
    """
    drug_name: string (case-insensitive)
    pgx_profile: output of build_pharmacogenomic_profile (per-gene dict)
    returns: dict { risk_assessment, primary_gene }
    """
    drug = drug_name.strip().upper()
    if drug not in _risk_rules:
        # Unknown drug - return Unknown label
        return {
            "risk_assessment": {
                "risk_label": "Unknown",
                "confidence_score": 0.0,
                "severity": "unknown"
            },
            "primary_gene": None
        }

    drug_rules = _risk_rules[drug]
    primary_gene = None
    assessment = None

    for gene_key, mapping in drug_rules.items():
        gene = gene_key
        if gene in pgx_profile:
            primary_gene = gene
            phenotype = pgx_profile[gene]["phenotype"]
            if not phenotype:
                return {
                    "risk_assessment": {
                        "risk_label": "Unknown",
                        "confidence_score": 0.0,
                        "severity": "unknown"
                    },
                    "primary_gene": gene
                }

            # Try direct phenotype mapping
            rule = mapping.get(phenotype)

            # Fallback normalization (SLCO1B1 etc.)
            if not rule:
                if phenotype == "NM" and mapping.get("NormalFunction"):
                    rule = mapping.get("NormalFunction")
                elif phenotype in ("PM","IM") and mapping.get("LowFunction"):
                    rule = mapping.get("LowFunction")
                else:
                    rule = {"risk_label":"Unknown","severity":"unknown","confidence":0.0}

            assessment = rule
            break

    if not assessment:
        assessment = {"risk_label":"Unknown","severity":"unknown","confidence":0.0}

    # ✅ Merge rule confidence + gene evidence confidence
    rule_conf = float(assessment.get("confidence", 0.0))
    gene_conf = float(pgx_profile.get(primary_gene, {}).get("confidence", 0.5)) if primary_gene else 0.5

    final_conf = round((rule_conf + gene_conf) / 2, 2)

    return {
        "risk_assessment": {
            "risk_label": assessment.get("risk_label"),
            "confidence_score": final_conf,
            "severity": assessment.get("severity")
        },
        "primary_gene": primary_gene
    }
