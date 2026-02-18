from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal
from openai import OpenAI
import json

from pdf_extract import extract_text_from_pdf_bytes

# OpenAI client (utilise env OPENAI_API_KEY)
client = OpenAI()

app = FastAPI(title="PDF Extractor API")

# Autoriser Angular en dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Pydantic models
# -------------------------

class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=20)

class AnalyzeResponse(BaseModel):
    titre: str
    resume: str
    mots_cles: list[str]
    type_document: Literal["facture", "contrat", "article", "rapport", "cv", "autre"]
    langue: Literal["fr", "en", "autre"]

class ProcessResponse(BaseModel):
    filename: str
    chars: int
    ocr_used: bool
    analysis: AnalyzeResponse


# -------------------------
# Helpers
# -------------------------

def analyze_with_llm(text: str) -> AnalyzeResponse:
    # Limiter pour éviter d'envoyer des documents énormes (chunking en bonus plus tard)
    text_for_llm = text[:12000]

    prompt = f"""
Tu es un assistant qui analyse un document.
Retourne UNIQUEMENT un JSON valide (sans texte autour), suivant exactement ce schéma:

{{
  "titre": "Titre du document ou titre suggéré",
  "resume": "Résumé du contenu en 2-3 phrases",
  "mots_cles": ["mot1", "mot2", "mot3"],
  "type_document": "facture | contrat | article | rapport | cv | autre",
  "langue": "fr | en | autre"
}}

Règles:
- JSON strict, guillemets doubles, pas de texte avant/après, pas de markdown.
- mots_cles: 3 à 8 mots max.
- type_document doit être UNE des valeurs: facture, contrat, article, rapport, cv, autre
- langue: "fr" si le texte est en français, "en" si anglais.

Texte du document:
\"\"\"{text_for_llm}\"\"\"
""".strip()

    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu produis uniquement du JSON valide."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    content = (resp.choices[0].message.content or "").strip()

    # Parse JSON brut
    try:
        data = json.loads(content)
    except Exception:
        raise ValueError(f"Réponse LLM non-JSON: {content[:500]}")

    # Validation stricte via Pydantic
    return AnalyzeResponse(**data)


# -------------------------
# Routes
# -------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF.")

    pdf_bytes = await file.read()

    try:
        text, ocr_used = extract_text_from_pdf_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {
        "filename": file.filename,
        "text": text,
        "chars": len(text),
        "ocr_used": ocr_used
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest):
    try:
        return analyze_with_llm(payload.text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))

@app.post("/process", response_model=ProcessResponse)
async def process(file: UploadFile = File(...)):
    """
    Endpoint final attendu côté front:
    Upload PDF -> extract (pypdf/OCR) -> analyze (OpenAI) -> JSON structuré
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF.")

    pdf_bytes = await file.read()

    # 1) Extract
    try:
        text, ocr_used = extract_text_from_pdf_bytes(pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Extraction error: {e}")

    # 2) Analyze
    try:
        analysis = analyze_with_llm(text)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"LLM error: {e}")

    return ProcessResponse(
        filename=file.filename,
        chars=len(text),
        ocr_used=ocr_used,
        analysis=analysis
    )
