#!/usr/bin/env python3
"""
Script para extrair PDFs usando PyMuPDF (fitz) - Funciona melhor com PDFs digitalizados
"""
import os
import json
from pathlib import Path
from datetime import datetime

def install_dependencies():
    deps = [
        "PyMuPDF",
        "langchain",
        "langchain-community",
        "sentence-transformers",
        "faiss-cpu"
    ]
    for dep in deps:
        try:
            if dep == "PyMuPDF":
                import fitz
            else:
                __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando {dep}...")
            os.system(f"pip install {dep}")

def extract_with_pymupdf():
    print("🚀 Extraindo PDFs com PyMuPDF + LangChain + Hugging Face...")
    try:
        import fitz  # PyMuPDF
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.schema import Document
        
        uploads_dir = Path("uploads")
        all_documents = []
        extracted_results = {}
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        for pdf_file in uploads_dir.glob("*.pdf"):
            print(f"\n📄 Processando com PyMuPDF: {pdf_file.name}")
            try:
                # Abrir PDF com PyMuPDF
                doc = fitz.open(str(pdf_file))
                print(f"   📑 Páginas encontradas: {len(doc)}")
                
                full_text = ""
                page_texts = []
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    
                    # Tentar extrair texto normal primeiro
                    page_text = page.get_text()
                    
                    # Se não há texto, tentar extrair como imagem (OCR básico)
                    if len(page_text.strip()) < 50:
                        print(f"   🖼️ Página {page_num+1} parece ser imagem, tentando extração...")
                        # Extrair texto de elementos gráficos e imagens
                        blocks = page.get_text("dict")["blocks"]
                        for block in blocks:
                            if "lines" in block:
                                for line in block["lines"]:
                                    for span in line["spans"]:
                                        page_text += span["text"] + " "
                    
                    page_texts.append(page_text)
                    full_text += f"\n--- PÁGINA {page_num+1} ---\n{page_text}"
                    print(f"   📄 Página {page_num+1}: {len(page_text)} caracteres")
                
                doc.close()
                
                print(f"   📊 Total de caracteres extraídos: {len(full_text)}")
                
                # Buscar por termos específicos ANTES de processar chunks
                julia_found = False
                julia_contexts = []
                
                if "JULIA CAROLINA BORGES" in full_text.upper():
                    julia_found = True
                    print(f"   🎯 ENCONTRADO: 'JULIA CAROLINA BORGES' em {pdf_file.name}!")
                    
                    # Encontrar contextos onde aparece
                    lines = full_text.split('\n')
                    for line_num, line in enumerate(lines):
                        if "JULIA CAROLINA BORGES" in line.upper():
                            context_start = max(0, line_num - 3)
                            context_end = min(len(lines), line_num + 4)
                            context = '\n'.join(lines[context_start:context_end])
                            julia_contexts.append({
                                "linha": line_num,
                                "contexto": context.strip()
                            })
                    
                    for i, ctx in enumerate(julia_contexts):
                        print(f"   📝 Contexto {i+1}:")
                        print(f"   {ctx['contexto']}")
                        print("   " + "-"*50)
                
                # Salvar resultado da busca
                extracted_results[pdf_file.name] = {
                    "total_chars": len(full_text),
                    "total_pages": len(page_texts),
                    "julia_found": julia_found,
                    "julia_contexts": julia_contexts,
                    "chars_per_page": [len(p) for p in page_texts]
                }
                
                if len(full_text.strip()) > 100:
                    chunks = text_splitter.split_text(full_text)
                    print(f"   🧩 Chunks criados: {len(chunks)}")
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 50:
                            doc_obj = Document(
                                page_content=chunk,
                                metadata={
                                    "source_file": pdf_file.name,
                                    "chunk_index": i,
                                    "extraction_method": "pymupdf",
                                    "julia_found": julia_found
                                }
                            )
                            all_documents.append(doc_obj)
                    
                    # Salvar texto extraído
                    output_file = f"data/extracted_texts/{pdf_file.stem}_pymupdf.txt"
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"   💾 Texto salvo em: {output_file}")
                    
                else:
                    print(f"   ⚠️ Pouco texto extraído de {pdf_file.name}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar {pdf_file.name}: {str(e)}")
                extracted_results[pdf_file.name] = {
                    "error": str(e),
                    "julia_found": False
                }
        
        # Salvar relatório de busca
        search_report = {
            "search_term": "JULIA CAROLINA BORGES",
            "search_date": datetime.now().isoformat(),
            "files_processed": extracted_results,
            "total_documents_created": len(all_documents)
        }
        
        report_file = "data/artifacts/julia_search_report.json"
        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(search_report, f, indent=2, ensure_ascii=False)
        print(f"\n📋 Relatório de busca salvo em: {report_file}")
        
        # Resumo da busca
        julia_files = [f for f, data in extracted_results.items() if data.get('julia_found', False)]
        if julia_files:
            print(f"\n🎯 RESUMO: 'JULIA CAROLINA BORGES' encontrada em {len(julia_files)} arquivo(s):")
            for file in julia_files:
                contexts = len(extracted_results[file].get('julia_contexts', []))
                print(f"   ✅ {file} ({contexts} ocorrência(s))")
        else:
            print(f"\n❌ 'JULIA CAROLINA BORGES' NÃO foi encontrada em nenhum arquivo.")
        
        if not all_documents:
            print("❌ Nenhum documento extraído para embeddings.")
            return
            
        print(f"\n🧠 Gerando embeddings com Hugging Face...")
        print(f"📊 Total de documentos: {len(all_documents)}")
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(all_documents, embeddings)
        vectorstore_path = "data/vectorstore/pymupdf_hf"
        Path(vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(vectorstore_path)
        print(f"✅ Vector store salvo em: {vectorstore_path}")
        print(f"\n🔍 Pronto para consultas semânticas!")
        
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔄 Instalando dependências...")
        install_dependencies()
        print("🔁 Execute o script novamente após a instalação.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    print("="*60)
    print("🔧 EXTRAÇÃO COM PYMUPDF + LANGCHAIN + HF")
    print("="*60)
    extract_with_pymupdf()
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
