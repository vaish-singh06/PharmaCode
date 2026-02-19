import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RULES_DIR = BASE / "rules"

_cpic = json.loads((RULES_DIR / "cpic_rules.json").read_text())

def get_clinical_recommendation(drug_name, primary_gene, phenotype):
    drug = drug_name.strip().upper()
    if drug not in _cpic:
        return {"text": "No pharmacogenomic evidence detected to determine recommendation."}


    gene_block = _cpic[drug]
    # gene block keys may be combined names, find best match
    if primary_gene in gene_block:
        rec = gene_block[primary_gene].get(phenotype)
        if rec:
            return {"text": rec}
    # fallback: if only one gene in block, try that
    for k,v in gene_block.items():
        rec = v.get(phenotype)
        if rec:
            return {"text": rec}

    return {"text": "No specific CPIC recommendation for this genotype/phenotype combination."}
