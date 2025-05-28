#!/usr/bin/env python3
"""
Script para extrair PDFs com OCR usando LangChain + Tesseract + Hugging Face Embeddings
"""
import os
import json
from pathlib import Path
from datetime import datetime

def install_dependencies():
    deps = [
        "langchain",
        "langchain-community", 
        "pypdf",
        "pdf2image",
        "pytesseract",
        "sentence-transformers",
        "faiss-cpu",
        "pillow"
    ]
    for dep in deps:
        try:
            if dep == "pdf2image":
                import pdf2image
            elif dep == "pytesseract":
                import pytesseract
            else:
                __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando {dep}...")
            os.system(f"pip install {dep}")

def extract_with_ocr():
    print("🚀 Extraindo PDFs com OCR + LangChain + Hugging Face...")
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.schema import Document
        
        uploads_dir = Path("uploads")
        all_documents = []
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        for pdf_file in uploads_dir.glob("*.pdf"):
            print(f"\n📄 Processando com OCR: {pdf_file.name}")
            try:
                # Converter PDF para imagens
                print("   🖼️ Convertendo páginas para imagem...")
                images = convert_from_path(str(pdf_file))
                print(f"   📸 {len(images)} imagens criadas")
                
                full_text = ""
                for i, image in enumerate(images):
                    print(f"   🔍 OCR na página {i+1}/{len(images)}...")
                    # Extrair texto com OCR
                    page_text = pytesseract.image_to_string(image, lang='por')
                    full_text += f"\n--- PÁGINA {i+1} ---\n{page_text}"
                
                print(f"   📊 Caracteres extraídos com OCR: {len(full_text)}")
                
                if len(full_text.strip()) > 100:  # Pelo menos 100 caracteres
                    chunks = text_splitter.split_text(full_text)
                    print(f"   🧩 Chunks criados: {len(chunks)}")
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:  # Chunks menores para OCR
                            doc = Document(
                                page_content=chunk,
                                metadata={
                                    "source_file": pdf_file.name,
                                    "chunk_index": i,
                                    "extraction_method": "ocr_langchain_hf"
                                }
                            )
                            all_documents.append(doc)
                    
                    # Buscar por termos específicos
                    if "JULIA CAROLINA BORGES" in full_text.upper():
                        print(f"   🎯 ENCONTRADO: 'JULIA CAROLINA BORGES' em {pdf_file.name}!")
                        # Encontrar contexto
                        lines = full_text.split('\n')
                        for line_num, line in enumerate(lines):
                            if "JULIA CAROLINA BORGES" in line.upper():
                                context_start = max(0, line_num - 2)
                                context_end = min(len(lines), line_num + 3)
                                context = '\n'.join(lines[context_start:context_end])
                                print(f"   📝 Contexto encontrado:\n{context}")
                    
                    # Salvar texto extraído
                    output_file = f"data/extracted_texts/{pdf_file.stem}_ocr.txt"
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"   💾 Texto OCR salvo em: {output_file}")
                    
                else:
                    print(f"   ⚠️ Pouco texto extraído de {pdf_file.name}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {pdf_file.name}: {str(e)}")
        
        if not all_documents:
            print("❌ Nenhum documento extraído.")
            return
            
        print(f"\n🧠 Gerando embeddings com Hugging Face...")
        print(f"📊 Total de documentos: {len(all_documents)}")
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(all_documents, embeddings)
        vectorstore_path = "data/vectorstore/ocr_langchain_hf"
        Path(vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(vectorstore_path)
        print(f"✅ Vector store salvo em: {vectorstore_path}")
        print(f"\nPronto para consultas semânticas!")
        
        # Salvar resumo
        summary = {
            "extracted_at": datetime.now().isoformat(),
            "total_documents": len(all_documents),
            "extraction_method": "ocr_langchain_hf",
            "files_processed": [f.name for f in uploads_dir.glob("*.pdf")]
        }
        
        summary_file = "data/artifacts/ocr_extraction_summary.json"
        Path(summary_file).parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"📋 Resumo salvo em: {summary_file}")
        
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔄 Instalando dependências...")
        install_dependencies()
        print("🔁 Execute o script novamente após a instalação.")
        print("⚠️ NOTA: Para OCR, você também precisa instalar o Tesseract:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux: apt-get install tesseract-ocr tesseract-ocr-por")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    print("="*60)
    print("🔧 EXTRAÇÃO COM OCR + LANGCHAIN + HF")
    print("="*60)
    extract_with_ocr()
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
