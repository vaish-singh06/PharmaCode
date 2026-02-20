# 🧬 PharmaGuard — Pharmacogenomic Risk Prediction System

PharmaGuard is an AI-powered web application built for the **RIFT 2026 Hackathon** that analyzes patient genetic data (VCF files) and predicts **drug-specific risks** using pharmacogenomics. The system provides **clinically actionable recommendations** aligned with CPIC guidelines and generates **explainable AI insights** to support safer, personalized medicine.

---
   
## 🌐 Live Demo

👉 Deployed Application:  
https://pharma-code.vercel.app/

---

## 🎥 Demo Video (LinkedIn)

👉 Project Demo Video:  
https://www.linkedin.com/posts/omkar-chavan-8b59a8334_rift2026-pharmaguard-pharmacogenomics-ugcPost-7430436591375986689-f_E-?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFQnEQkBZ9hTepbDydPe3LWCmZM6dT7V0to

---

## 🧠 Problem Overview

Adverse drug reactions cause serious harm and even death in many patients every year. One major reason is **genetic variation** that affects how individuals metabolize drugs.

PharmaGuard solves this by:
- Parsing VCF (Variant Call Format) files
- Identifying pharmacogenomic variants
- Mapping genes to drug response phenotypes
- Predicting risk categories:
  - Safe
  - Adjust Dosage
  - Toxic
  - Ineffective
  - Unknown
- Providing clinical recommendations and LLM-generated explanations

---

## 🏗️ Architecture Overview

**Workflow:**
1. User uploads VCF file and enters drug name(s)
2. Backend:
   - Validates and parses VCF
   - Extracts variants (GENE, STAR, rsID)
   - Maps genotype to phenotype
   - Applies drug–gene risk rules
   - Generates clinical recommendation
   - Uses LLM for explanation
   - Builds structured JSON output
3. Frontend:
   - Displays color-coded risk result
   - Shows recommendation and explanation
   - Allows JSON copy and download

**High-Level Architecture:**
Frontend (React) → Backend (FastAPI) → VCF Parser + Risk Engine + LLM → JSON Response → UI

---

## 🛠️ Tech Stack

**Frontend:**
- React
- Axios
- HTML/CSS

**Backend:**
- Python
- FastAPI
- Uvicorn

**AI / Logic:**
- Rule-based pharmacogenomic risk engine
- LLM for explanation generation

**Deployment:**
- Vercel

---

## ⚙️ Installation Instructions (Local Setup)

### 1️⃣ Clone the Repository

git clone https://github.com/vaish-singh06/pharma-code.git
cd pharma-code
2️⃣ Backend Setup
cd backend
python -m venv venv
venv\Scripts\activate   # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

Backend will run at:
http://127.0.0.1:8000

3️⃣ Frontend Setup
cd ../frontend
npm install
npm start

Frontend will run at:
http://localhost:3000

📡 API Documentation
POST /analyze/

Description:
Analyzes uploaded VCF file and drug input to return pharmacogenomic risk assessment.

Request:

Method: POST

Content-Type: multipart/form-data

Fields:

file: VCF file

drug: Drug name(s), comma-separated

Response:

JSON object containing:

patient_id

drug

timestamp

risk_assessment

pharmacogenomic_profile

clinical_recommendation

llm_generated_explanation

quality_metrics

🧪 Usage Examples
Example Steps:

Open the web app: https://pharma-code.vercel.app/

Upload a VCF file

Enter a drug name (e.g., CODEINE, WARFARIN)

Click Analyze

View:

Risk label (Safe / Adjust / Toxic / Ineffective / Unknown)

Gene and phenotype

Clinical recommendation

AI-generated explanation

Copy or download the JSON output

💊 Supported Drugs

CODEINE (CYP2D6)

WARFARIN (CYP2C9)

CLOPIDOGREL (CYP2C19)

SIMVASTATIN (SLCO1B1)

AZATHIOPRINE (TPMT)

FLUOROURACIL (DPYD)

👥 Team Members

Vaishnavi Chandel

Omkar Chavan

Ritu Krishnan

Sneha Kumari 
