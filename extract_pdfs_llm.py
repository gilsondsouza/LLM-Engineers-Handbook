#!/usr/bin/env python3
"""
Script para extrair texto de todos os PDFs da pasta uploads usando LLM (PyPDF2)
"""
import os
from pathlib import Path
import PyPDF2
import json
from datetime import datetime

UPLOADS_DIR = Path("uploads")
OUTPUT_FILE = "data/artifacts/extracted_pdfs.json"


def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
    except Exception as e:
        print(f"Erro ao extrair {pdf_path}: {e}")
        return None

def main():
    print("=== Extração de PDFs com LLM ===")
    results = []
    for file in UPLOADS_DIR.glob("*.pdf"):
        print(f"Extraindo: {file.name}")
        text = extract_text_from_pdf(file)
        if text:
            result = {
                "filename": file.name,
                "filepath": str(file),
                "extracted_at": datetime.now().isoformat(),
                "char_count": len(text),
                "text": text
            }
            results.append(result)
            print(f"✓ {file.name} extraído com sucesso ({len(text)} caracteres)")
        else:
            print(f"✗ Falha ao extrair {file.name}")
    # Salvar resultados
    if results:
        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nTodos os PDFs extraídos e salvos em {OUTPUT_FILE}")
    else:
        print("Nenhum PDF extraído.")

if __name__ == "__main__":
    main()
