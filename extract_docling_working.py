#!/usr/bin/env python3
"""
Script para extrair PDFs usando Docling + Hugging Face Embeddings
"""
import os
import json
from pathlib import Path
from datetime import datetime

def install_dependencies():
    deps = [
        "docling",
        "sentence-transformers",
        "faiss-cpu"
    ]
    for dep in deps:
        try:
            if dep == "docling":
                from docling.document_converter import DocumentConverter
            elif dep == "sentence-transformers":
                from sentence_transformers import SentenceTransformer
            elif dep == "faiss-cpu":
                import faiss
        except ImportError:
            print(f"📦 Instalando {dep}...")
            if dep == "docling":
                os.system("pip install docling")
            else:
                os.system(f"pip install {dep}")

def extract_with_docling():
    print("🚀 Extraindo PDFs com Docling + Hugging Face...")
    try:
        from docling.document_converter import DocumentConverter
        from sentence_transformers import SentenceTransformer
        import faiss
        import numpy as np
        
        uploads_dir = Path("uploads")
        all_documents = []
        extracted_results = {}
        
        # Inicializar o conversor Docling
        converter = DocumentConverter()
        
        for pdf_file in uploads_dir.glob("*.pdf"):
            print(f"\n📄 Processando com Docling: {pdf_file.name}")
            try:
                # Converter PDF com Docling
                print("   🔄 Convertendo documento...")
                result = converter.convert(str(pdf_file))
                
                # Extrair texto do resultado
                full_text = result.document.export_to_markdown()
                print(f"   📊 Caracteres extraídos: {len(full_text)}")
                
                # Buscar por termos específicos
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
                    "julia_found": julia_found,
                    "julia_contexts": julia_contexts,
                    "extraction_method": "docling"
                }
                
                if len(full_text.strip()) > 100:
                    # Dividir texto em chunks
                    chunk_size = 1000
                    chunks = []
                    for i in range(0, len(full_text), chunk_size):
                        chunk = full_text[i:i+chunk_size]
                        if len(chunk.strip()) > 50:
                            chunks.append({
                                "text": chunk,
                                "metadata": {
                                    "source_file": pdf_file.name,
                                    "chunk_index": len(chunks),
                                    "extraction_method": "docling",
                                    "julia_found": julia_found
                                }
                            })
                    
                    all_documents.extend(chunks)
                    print(f"   🧩 Chunks criados: {len(chunks)}")
                    
                    # Salvar texto extraído
                    output_file = f"data/extracted_texts/{pdf_file.stem}_docling.txt"
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"   💾 Texto salvo em: {output_file}")
                    
                    # Salvar também como Markdown
                    md_file = f"data/extracted_texts/{pdf_file.stem}_docling.md"
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"   📝 Markdown salvo em: {md_file}")
                    
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
            "extraction_method": "docling",
            "files_processed": extracted_results,
            "total_documents_created": len(all_documents)
        }
        
        report_file = "data/artifacts/docling_julia_search_report.json"
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
        
        # Carregar modelo de embeddings
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Gerar embeddings
        texts = [doc["text"] for doc in all_documents]
        embeddings = model.encode(texts, show_progress_bar=True)
        
        # Criar índice FAISS
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        
        # Normalizar embeddings para cosine similarity
        faiss.normalize_L2(embeddings)
        index.add(embeddings.astype('float32'))
        
        # Salvar índice e metadados
        vectorstore_path = "data/vectorstore/docling_hf"
        Path(vectorstore_path).mkdir(parents=True, exist_ok=True)
        
        faiss.write_index(index, str(Path(vectorstore_path) / "index.faiss"))
        
        # Salvar metadados dos documentos
        metadata = {
            "documents": all_documents,
            "model_name": "sentence-transformers/all-MiniLM-L6-v2",
            "dimension": dimension,
            "total_docs": len(all_documents)
        }
        
        with open(Path(vectorstore_path) / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Vector store salvo em: {vectorstore_path}")
        print(f"🔍 Pronto para consultas semânticas!")
        
        # Exemplo de busca semântica
        if julia_files:
            print(f"\n🔍 Teste de busca semântica por 'JULIA CAROLINA BORGES':")
            query = "JULIA CAROLINA BORGES"
            query_embedding = model.encode([query])
            faiss.normalize_L2(query_embedding)
            
            scores, indices = index.search(query_embedding.astype('float32'), k=3)
            
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(all_documents):
                    doc = all_documents[idx]
                    print(f"   {i+1}. Score: {score:.4f} | Arquivo: {doc['metadata']['source_file']}")
                    preview = doc['text'][:200].replace('\n', ' ')
                    print(f"      Preview: {preview}...")
        
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔄 Instalando dependências...")
        install_dependencies()
        print("🔁 Execute o script novamente após a instalação.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("="*60)
    print("🔧 EXTRAÇÃO COM DOCLING + HUGGING FACE")
    print("="*60)
    extract_with_docling()
    print("\n✅ Processo concluído!")

if __name__ == "__main__":
    main()
