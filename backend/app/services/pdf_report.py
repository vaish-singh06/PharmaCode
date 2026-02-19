from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from datetime import datetime
import os


# ✅ Clinical Color Semantics
RISK_COLORS = {
    "Safe": colors.green,
    "Adjust Dosage": colors.orange,
    "Toxic": colors.red,
    "Ineffective": colors.red,
    "Unknown": colors.grey
}


def build_pdf_report(results, output_path):

    doc = SimpleDocTemplate(output_path, pagesize=A4)

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "Title",
        fontSize=18,
        spaceAfter=20,
        textColor=colors.black
    )

    section_header = ParagraphStyle(
        "Header",
        fontSize=12,
        spaceAfter=6,
        textColor=colors.black
    )

    normal = ParagraphStyle(
        "Normal",
        fontSize=10,
        spaceAfter=4
    )

    small = ParagraphStyle(
        "Small",
        fontSize=9,
        textColor=colors.grey
    )

    elements = []

    # ✅ Report Title
    elements.append(Paragraph("Pharmacogenomic Clinical Report", title_style))
    elements.append(
        Paragraph(
            f"Generated: {datetime.utcnow().replace(microsecond=0).isoformat()}Z",
            small
        )
    )

    elements.append(Spacer(1, 12))

    # ✅ Patient Info (single patient assumed)
    patient_id = results[0]["patient_id"]

    elements.append(Paragraph("<b>Patient Information</b>", section_header))
    elements.append(Paragraph(f"Patient ID: {patient_id}", normal))

    elements.append(Spacer(1, 12))

    # ✅ Drug Sections
    elements.append(Paragraph("<b>Drug Risk Summary</b>", section_header))

    for r in results:

        drug = r["drug"]
        risk = r["risk_assessment"]["risk_label"]
        severity = r["risk_assessment"]["severity"]

        pgx = r["pharmacogenomic_profile"]

        gene = pgx.get("primary_gene")
        diplotype = pgx.get("diplotype")
        phenotype = pgx.get("phenotype")
        activity_score = pgx.get("activity_score")

        recommendation = r["clinical_recommendation"]["text"]
        interpretation = r.get("drug_level_interpretation")

        risk_color = RISK_COLORS.get(risk, colors.black)

        elements.append(Spacer(1, 10))

        # ✅ Drug Header
        elements.append(
            Paragraph(
                f"<b>Drug:</b> {drug}",
                section_header
            )
        )

        # ✅ Risk Line (color coded)
        elements.append(
            Paragraph(
                f"<b>Risk Assessment:</b> "
                f"<font color='{risk_color}'>"
                f"{risk} ({severity})"
                f"</font>",
                normal
            )
        )

        # ✅ Table for PGx Data
        table_data = [
            ["Primary Gene", gene],
            ["Diplotype", diplotype],
            ["Phenotype", phenotype],
            ["Activity Score", str(activity_score)]
        ]

        table = Table(table_data, hAlign="LEFT")

        table.setStyle(TableStyle([
            ("FONT", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)

        elements.append(Spacer(1, 6))

        # ✅ Clinical Recommendation
        elements.append(
            Paragraph(
                f"<b>Clinical Recommendation:</b> {recommendation}",
                normal
            )
        )

        # ✅ Drug-Level Interpretation ⭐⭐⭐⭐⭐
        if interpretation:
            elements.append(
                Paragraph(
                    f"<b>Clinical Interpretation:</b> {interpretation}",
                    normal
                )
            )

        # ✅ LLM Explanation (Summary Only — clinical realism)
        llm_summary = r["llm_generated_explanation"]["summary"]

        elements.append(
            Paragraph(
                f"<b>Mechanistic Rationale:</b> {llm_summary}",
                normal
            )
        )

    doc.build(elements)
