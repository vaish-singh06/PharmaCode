from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.analyzer import run_analysis_from_path
from fastapi.concurrency import run_in_threadpool
import tempfile, os, uuid

router = APIRouter()

SUPPORTED_DRUGS = [
    "CODEINE",
    "WARFARIN",
    "CLOPIDOGREL",
    "SIMVASTATIN",
    "AZATHIOPRINE",
    "FLUOROURACIL"
]

MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def normalize_drug_name(d):
    d = d.strip().upper()

    corrections = {
        "CODOINE": "CODEINE"  # typo guard
    }

    if d in corrections:
        return corrections[d]

    if d not in SUPPORTED_DRUGS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported drug: {d}"
        )

    return d


@router.post("/")
async def analyze_vcf(
    file: UploadFile = File(...),
    drug: str = Form(...)
):
    """
    Upload VCF + drug(s)
    Supports comma-separated drugs
    """

    # ✅ STREAMED FILE VALIDATION (NO MEMORY SPIKE)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".vcf")

    size = 0

    try:
        while True:
            chunk = await file.read(64 * 1024)  # 64 KB chunks
            if not chunk:
                break

            size += len(chunk)

            if size > MAX_BYTES:
                tmp.close()
                os.remove(tmp.name)
                raise HTTPException(
                    status_code=400,
                    detail="VCF exceeds 5 MB size limit."
                )

            tmp.write(chunk)

        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty file uploaded."
            )

        tmp.flush()
        tmp.close()

        tmp_path = tmp.name

        # ✅ Patient ID generated once per upload
        patient_id = str(uuid.uuid4())

        # ✅ Normalize multiple drugs
        drugs = [
            normalize_drug_name(d)
            for d in drug.split(",")
            if d.strip()
        ]

        if not drugs:
            raise HTTPException(
                status_code=400,
                detail="No valid drug provided."
            )

        results = []

        # ✅ Run blocking analysis safely
        for d in drugs:
            try:
                out = await run_in_threadpool(
                    run_analysis_from_path,
                    tmp_path,
                    d,
                    patient_id
                )
                results.append(out)

            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Analysis failed for drug {d}: {str(e)}"
                )

        # ✅ Return single object or list
        return results[0] if len(results) == 1 else results

    finally:
        # ✅ Guaranteed cleanup
        try:
            os.remove(tmp.name)
        except Exception:
            pass
