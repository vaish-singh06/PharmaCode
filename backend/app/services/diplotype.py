import json
from pathlib import Path
from collections import Counter

BASE = Path(__file__).resolve().parents[1]
RULES_DIR = BASE / "rules"

_diplotype_map = json.loads((RULES_DIR / "diplotype_map.json").read_text())
_allele_function = json.loads((RULES_DIR / "allele_function.json").read_text())
_rsid_star_map = json.loads((RULES_DIR / "rsid_star_map.json").read_text())

TARGET_GENES = list(_diplotype_map.keys())

FUNCTION_SCORES = {
    "no_function": 0.0,
    "decreased": 0.5,
    "normal": 1.0,
    "increased": 1.5
}


# ✅ CLINICAL INTERPRETATION ENGINE ⭐⭐⭐⭐⭐
def generate_clinical_interpretation(gene, phenotype, activity_score):

    if not phenotype:
        return "Insufficient genetic evidence to determine metabolic phenotype."

    phenotype_full = {
        "PM": "Poor Metabolizer",
        "IM": "Intermediate Metabolizer",
        "NM": "Normal Metabolizer",
        "RM": "Rapid Metabolizer",
        "UM": "Ultrarapid Metabolizer"
    }.get(phenotype, phenotype)

    base = f"{phenotype_full} phenotype predicted for {gene}. "

    # Gene-specific clinical framing
    if gene.startswith("CYP"):

        if phenotype == "PM":
            return base + \
                "Markedly reduced enzymatic activity expected. Drug metabolism may be significantly impaired."

        if phenotype == "IM":
            return base + \
                "Reduced metabolic capacity observed. Altered drug exposure or response variability may occur."

        if phenotype == "NM":
            return base + \
                "Enzymatic activity within expected physiological range."

        if phenotype in ("RM", "UM"):
            return base + \
                "Increased metabolic activity possible. Reduced drug exposure or therapeutic failure may occur."

    if gene in ("TPMT", "DPYD"):

        if phenotype == "PM":
            return base + \
                "Severely impaired drug detoxification capacity. High toxicity risk possible."

        if phenotype == "IM":
            return base + \
                "Partial reduction in enzymatic function. Dose adjustments may be clinically relevant."

        if phenotype == "NM":
            return base + \
                "Normal enzymatic function predicted."

    return base + \
        f"Activity Score = {activity_score}, supporting phenotype classification."


def infer_star_from_rsids(variants):

    gene_alleles = {g: [] for g in TARGET_GENES}

    for v in variants:

        gene = v.get("gene")
        if gene not in TARGET_GENES:
            continue

        # If the VCF already provided a STAR allele in INFO, respect that and apply multiplicity
        if v.get("star"):
            # if star provided once but genotype is homozygous, append twice
            star_val = v["star"]
            times = 1
            if v.get("is_homozygous"):
                times = 2
            for _ in range(times):
                gene_alleles[gene].append(star_val)
            continue

        # Try mapping by rsid -> star
        rsid = v.get("rsid")
        if rsid in _rsid_star_map:
            mapping = _rsid_star_map[rsid]
            if mapping.get("gene") == gene:
                allele_name = mapping["allele"]
                # determine multiplicity from allele_indices / alt_count (added by parser)
                alt_count = v.get("alt_count", None)
                if alt_count is None:
                    # fallback: if genotype string contains two same non-ref alleles, assume hom
                    gt = v.get("genotype", "")
                    if "/" in gt:
                        a, b = gt.split("/")
                        if a == b and a != "?":
                            alt_count = 2 if a != "0" else 0
                        else:
                            alt_count = 1 if (a != "0" or b != "0") else 0
                    else:
                        alt_count = 0

                # append allele `alt_count` times (0 => don't append)
                for _ in range(max(0, alt_count)):
                    gene_alleles[gene].append(allele_name)

    # Keep multiplicity as appended (homozygous => two entries)
    return {g: gene_alleles[g] for g in gene_alleles}


# ✅ ACTIVITY SCORE + TRACE DETAILS
def calculate_activity_score_with_trace(gene, alleles):

    fn_map = _allele_function.get(gene, {})

    trace_details = []
    total_score = 0.0

    for allele in alleles:

        function = fn_map.get(allele)

        if not function:
            # try without star prefix, then fallback to 'normal'
            function = fn_map.get(allele.strip("*"), None) or fn_map.get(allele.replace("*", ""), None) or "normal"

        score = FUNCTION_SCORES.get(function, 1.0)

        total_score += score

        trace_details.append({
            "allele": allele,
            "function": function,
            "score": score
        })

    return round(total_score, 2), trace_details


# ✅ PHENOTYPE RULE TRACE
def phenotype_from_activity_score(gene, activity_score):

    if gene == "CYP2D6":

        if activity_score == 0:
            return "PM", f"Activity Score = {activity_score} → Poor Metabolizer"
        elif activity_score <= 1.0:
            return "IM", f"Activity Score = {activity_score} → Intermediate Metabolizer"
        elif activity_score <= 2.25:
            return "NM", f"Activity Score = {activity_score} → Normal Metabolizer"
        else:
            return "UM", f"Activity Score = {activity_score} → Ultrarapid Metabolizer"

    if gene == "CYP2C19":

        if activity_score == 0:
            return "PM", f"Activity Score = {activity_score} → Poor Metabolizer"
        elif activity_score <= 1.0:
            return "IM", f"Activity Score = {activity_score} → Intermediate Metabolizer"
        elif activity_score <= 2.0:
            return "NM", f"Activity Score = {activity_score} → Normal Metabolizer"
        else:
            return "UM", f"Activity Score = {activity_score} → Ultrarapid Metabolizer"

    if gene in ("CYP2C9", "TPMT", "DPYD"):

        if activity_score == 0:
            return "PM", f"Activity Score = {activity_score} → Poor Metabolizer"
        elif activity_score < 2:
            return "IM", f"Activity Score = {activity_score} → Intermediate Metabolizer"
        else:
            return "NM", f"Activity Score = {activity_score} → Normal Metabolizer"

    return "NM", f"Activity Score = {activity_score} → Default phenotype applied"


# Helper: choose canonical ordering for diplotype (prefer *1 on left, then numeric)
def _canonical_pair(a, b):
    if a == b:
        return a, b
    if a == "*1" and b != "*1":
        return a, b
    if b == "*1" and a != "*1":
        return b, a

    def _num_key(x):
        # extract numeric part if possible for sensible ordering
        s = "".join(ch for ch in x if ch.isdigit())
        try:
            return int(s) if s else float("inf")
        except:
            return float("inf")

    if _num_key(a) <= _num_key(b):
        return a, b
    else:
        return b, a


# ✅ DIPLOTYPE + TRACE ENGINE
def call_diplotype_and_phenotype(gene, detected_alleles):

    gene_map = _diplotype_map.get(gene, {})

    # No variants -> wildtype
    if not detected_alleles:

        diplotype = "*1/*1"
        phenotype = "NM"
        activity_score = 2.0

        decision_trace = {
            "reason": "No variants detected",
            "assumed_diplotype": diplotype,
            "assumed_activity_score": activity_score,
            "phenotype_rule": f"{diplotype} → Normal Metabolizer (wildtype assumption)",
            "method": "Wildtype Default"
        }

        clinical_interpretation = generate_clinical_interpretation(
            gene,
            phenotype,
            activity_score
        )

        return diplotype, phenotype, activity_score, decision_trace, clinical_interpretation

    # If the inference provided multiplicity correctly, detected_alleles list will include duplicate entries for homozygous alt.
    # Use allele counts to reliably decide diplotype for diploid genome.
    counts = Counter(detected_alleles)

    # If only a single allele observed across all variants (but may have multiplicity in counts),
    # decide if homozygous or heterozygous with *1
    if len(counts) == 1:
        only_allele = next(iter(counts.keys()))
        ct = counts[only_allele]
        if ct >= 2:
            alleles = [only_allele, only_allele]
        else:
            # observed once -> assume *1/allele (heterozygous)
            alleles = ["*1", only_allele] if only_allele != "*1" else ["*1", "*1"]

    else:
        # multiple allele types present: pick the two most supported alleles
        most = counts.most_common()
        # If the top allele has count >=2 -> homozygous for top allele
        if most[0][1] >= 2:
            alleles = [most[0][0], most[0][0]]
        else:
            # pick top two distinct alleles (if only one distinct allele present, fill with *1)
            first = most[0][0]
            second = most[1][0] if len(most) > 1 else "*1"
            alleles = [first, second]

    # enforce canonical ordering for diplotype string (e.g., *1/*3 not *3/*1)
    left, right = _canonical_pair(alleles[0], alleles[1])
    diplotype = f"{left}/{right}"

    phenotype_lookup = gene_map.get(diplotype)

    activity_score, allele_trace = calculate_activity_score_with_trace(
        gene,
        [left, right]
    )

    if phenotype_lookup:

        phenotype = phenotype_lookup
        method = "Diplotype Lookup Table"
        phenotype_rule = f"{diplotype} → {phenotype} phenotype (CPIC diplotype mapping)"

    else:

        phenotype, phenotype_rule = phenotype_from_activity_score(
            gene,
            activity_score
        )
        method = "Activity Score Model"

    clinical_interpretation = generate_clinical_interpretation(
        gene,
        phenotype,
        activity_score
    )

    decision_trace = {
        "alleles": [left, right],
        "allele_details": allele_trace,
        "activity_score": activity_score,
        "phenotype_rule": phenotype_rule,
        "method": method
    }

    return diplotype, phenotype, activity_score, decision_trace, clinical_interpretation


# ✅ PROFILE BUILDER WITH TRACE + INTERPRETATION ⭐⭐⭐⭐⭐
def build_pharmacogenomic_profile(variants):

    gene_alleles = infer_star_from_rsids(variants)
    profile = {}

    for gene in TARGET_GENES:

        alleles = gene_alleles.get(gene, [])

        diplotype, phenotype, activity_score, decision_trace, clinical_interpretation = \
            call_diplotype_and_phenotype(gene, alleles)

        confidence = 0.65

        if alleles:
            confidence = 0.85

        if any(v.get("star") for v in variants if v.get("gene") == gene):
            confidence = 0.95

        if decision_trace["method"] == "Activity Score Model":
            confidence -= 0.1

        confidence = round(confidence, 2)

        profile[gene] = {
            "diplotype": diplotype,
            "phenotype": phenotype,
            "activity_score": activity_score,
            "decision_trace": decision_trace,
            "clinical_interpretation": clinical_interpretation,  # ⭐⭐⭐⭐⭐ NEW
            "confidence": confidence
        }

    return profile
