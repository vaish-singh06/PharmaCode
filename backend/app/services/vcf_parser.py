import vcfpy
import json
from pathlib import Path
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

TARGET_GENES = ["CYP2D6", "CYP2C19", "CYP2C9", "SLCO1B1", "TPMT", "DPYD"]

# Load rsID → gene mapping
BASE = Path(__file__).resolve().parents[1]
RULES_DIR = BASE 

try:
    _rsid_gene = json.loads((RULES_DIR / "rsid_gene_map.json").read_text())
except Exception as e:
    logger.warning(f"rsid_gene_map load failed: {e}")
    _rsid_gene = {}


def _clean_vcf(file_path: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".vcf")
    clean_path = tmp.name

    with open(file_path, "r", errors="ignore") as fin, open(clean_path, "w") as fout:
        for line in fin:
            if line.startswith("#"):
                fout.write(line)
                continue

            parts = line.strip().split()

            # Skip extremely broken rows
            if len(parts) < 8:
                continue

            # ⭐ Fix broken POS column
            chrom = parts[0]

            # Find rsID index
            rs_index = None
            for i, p in enumerate(parts):
                if p.startswith("rs"):
                    rs_index = i
                    break

            if rs_index is None:
                continue

            # POS should be token before rsID (last numeric)
            pos_tokens = parts[1:rs_index]
            pos = None
            for token in reversed(pos_tokens):
                if token.isdigit():
                    pos = token
                    break

            if pos is None:
                continue

            # Rebuild correct VCF row
            new_parts = [chrom, pos] + parts[rs_index:]

            # Ensure 10 columns
            if len(new_parts) >= 10:
                new_parts = new_parts[:10]
            else:
                continue

            fout.write("\t".join(new_parts) + "\n")

    return clean_path


# ⭐ ---------- MAIN PARSER ----------
def parse_vcf(file_path: str):
    # Clean VCF first (prevents vcfpy crash)
    safe_path = _clean_vcf(file_path)

    reader = vcfpy.Reader.from_path(safe_path)
    variants = []

    for record in reader:
        info = record.INFO or {}

        # ---------- GENE DETECTION ----------
        gene = info.get("GENE")
        if isinstance(gene, list):
            gene = gene[0]

        rsid = record.ID
        if isinstance(rsid, list):
            rsid = rsid[0]

        if not gene and rsid in _rsid_gene:
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
        allele_map = {"0": ref}

        alts = [a.value for a in record.ALT] if record.ALT else []
        for idx, alt_val in enumerate(alts, start=1):
            allele_map[str(idx)] = alt_val

        sep = "|" if "|" in gt else "/"
        tokens = gt.split(sep)

        if len(tokens) < 2:
            tokens = [tokens[0], "0"]

        a, b = tokens[0], tokens[1]

        allele_a = allele_map.get(a, "?") if a != "." else "?"
        allele_b = allele_map.get(b, "?") if b != "." else "?"

        genotype_str = f"{allele_a}/{allele_b}"

        # ---------- STAR ----------
        star = info.get("STAR")
        if isinstance(star, list):
            star = star[0]

        variants.append({
            "gene": gene,
            "rsid": rsid,
            "genotype": genotype_str,
            "star": star,
            "info": dict(info)
        })

    # Cleanup temp file
    try:
        os.remove(safe_path)
    except:
        pass

    return variants
