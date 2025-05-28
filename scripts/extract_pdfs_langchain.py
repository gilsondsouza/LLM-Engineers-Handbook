#!/usr/bin/env python3
"""
Script para extrair texto de PDFs usando LangChain (PDFLoader)
Salva o texto extraído em arquivos .txt e em um JSON consolidado.
"""

import os
import json
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

UPLOADS_DIR = Path("uploads")
OUTPUT_DIR = Path("data/artifacts/pdf_extracted")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

results = []

for pdf_file in UPLOADS_DIR.glob("*.pdf"):
    print(f"Extraindo: {pdf_file.name}")
    try:
        loader = PyPDFLoader(str(pdf_file))
        docs = loader.load()
        full_text = "\n".join([doc.page_content for doc in docs])
        
        # Salvar texto em arquivo .txt
        txt_path = OUTPUT_DIR / f"{pdf_file.stem}.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        
        # Adicionar ao resultado consolidado
        results.append({
            "filename": pdf_file.name,
            "text_file": str(txt_path),
            "text_excerpt": full_text[:500],
            "char_count": len(full_text)
        })
        print(f"✓ Texto extraído e salvo em: {txt_path}")
    except Exception as e:
        print(f"✗ Erro ao extrair {pdf_file.name}: {str(e)}")

# Salvar resultado consolidado
json_path = OUTPUT_DIR / "pdf_extraction_summary.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nResumo salvo em: {json_path}")
