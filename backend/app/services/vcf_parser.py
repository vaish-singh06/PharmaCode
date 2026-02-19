import vcfpy
import json
from pathlib import Path

TARGET_GENES = ["CYP2D6","CYP2C19","CYP2C9","SLCO1B1","TPMT","DPYD"]

# Load rsID → gene mapping
BASE = Path(__file__).resolve().parents[1]
RULES_DIR = BASE / "rules"

try:
    _rsid_gene = json.loads((RULES_DIR / "rsid_gene_map.json").read_text())
except:
    _rsid_gene = {}

def parse_vcf(file_path: str):
    reader = vcfpy.Reader.from_path(file_path)
    variants = []

    for record in reader:
        info = record.INFO or {}

        # ---------- GENE DETECTION ----------
        # 1) Try INFO tag first (synthetic VCF support)
        gene = info.get("GENE")
        if isinstance(gene, list):
            gene = gene[0]

        # 2) If missing, fallback to rsID → gene mapping (real GIAB VCF support)
        rsid = record.ID
        if isinstance(rsid, list):
            rsid = rsid[0]

        if not gene and rsid in _rsid_gene:
            gene = _rsid_gene.get(rsid)

        # Skip non-target genes
        if not gene:
            gene = _rsid_gene.get(rsid)

        if gene not in TARGET_GENES:
            continue

        if not rsid:
            rsid = "Unknown"

        # ---------- SAFE GENOTYPE EXTRACTION ----------
        gt = "0/0"
        if record.calls:
            call = record.calls[0]
            gt = call.data.get("GT", "0/0")

        ref = record.REF

        # Build allele map correctly for ALL ALT alleles
        allele_map = {"0": ref}

        alts = [a.value for a in record.ALT] if record.ALT else []
        for idx, alt_val in enumerate(alts, start=1):
            allele_map[str(idx)] = alt_val

        # Normalize genotype separators
        sep = "/"
        if "|" in gt:
            sep = "|"

        tokens = gt.split(sep)

        # Handle malformed / missing GT
        if len(tokens) < 2:
            tokens = [tokens[0], "0"]

        a, b = tokens[0], tokens[1]

        # Handle missing alleles (./.)
        allele_a = allele_map.get(a, "?") if a != "." else "?"
        allele_b = allele_map.get(b, "?") if b != "." else "?"

        genotype_str = f"{allele_a}/{allele_b}"

        # ---------- STAR ALLELE ----------
        star = info.get("STAR")
        if isinstance(star,list):
            star = star[0]

        # ---------- VARIANT OBJECT ----------
        variants.append({
            "gene": gene,
            "rsid": rsid,
            "genotype": genotype_str,
            "star": star,
            "info": dict(info)
        })

    return variants
