from fastapi import APIRouter, Body
from fastapi.responses import FileResponse
from app.services.pdf_report import build_pdf_report
import tempfile

router = APIRouter()

@router.post("/")
async def generate_report(results: list = Body(...)):  

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    build_pdf_report(results, tmp.name)

    return FileResponse(
        tmp.name,
        media_type="application/pdf",
        filename="clinical_report.pdf"
    )
