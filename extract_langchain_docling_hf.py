#!/usr/bin/env python3
"""
Script para extrair PDFs usando LangChain + Docling + Hugging Face Embeddings
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
        "pdfplumber",
        "docling",
        "sentence-transformers",
        "faiss-cpu"
    ]
    for dep in deps:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            print(f"📦 Instalando {dep}...")
            os.system(f"pip install {dep}")

def extract_and_embed():
    print("🚀 Extraindo PDFs com LangChain + Docling + Hugging Face...")
    try:
        from langchain_community.document_loaders import PyPDFLoader
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
            print(f"\n📄 Processando: {pdf_file.name}")
            try:
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                print(f"   📑 Páginas carregadas: {len(documents)}")
                
                full_text = "\n".join([doc.page_content for doc in documents])
                print(f"   📊 Caracteres extraídos: {len(full_text)}")
                
                if len(full_text.strip()) > 0:
                    chunks = text_splitter.split_text(full_text)
                    print(f"   🧩 Chunks criados: {len(chunks)}")
                    
                    for i, chunk in enumerate(chunks):
                        if len(chunk.strip()) > 0:
                            doc = Document(
                                page_content=chunk,
                                metadata={
                                    "source_file": pdf_file.name,
                                    "chunk_index": i,
                                    "extraction_method": "langchain_docling_hf"
                                }
                            )
                            all_documents.append(doc)
                    
                    # Buscar por termos específicos
                    if "JULIA CAROLINA BORGES" in full_text.upper():
                        print(f"   🎯 ENCONTRADO: 'JULIA CAROLINA BORGES' em {pdf_file.name}!")
                    
                    # Salvar texto extraído
                    output_file = f"data/extracted_texts/{pdf_file.stem}_extracted.txt"
                    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(full_text)
                    print(f"   💾 Texto salvo em: {output_file}")
                    
                else:
                    print(f"   ⚠️ Nenhum texto extraído de {pdf_file.name}")
                      except Exception as e:
                print(f"   ❌ Erro ao processar {pdf_file.name}: {str(e)}")
        
        if not all_documents:
            print("❌ Nenhum documento extraído.")
            return
        print(f"\n🧠 Gerando embeddings com Hugging Face...")
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(all_documents, embeddings)
        vectorstore_path = "data/vectorstore/langchain_docling_hf"
        Path(vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(vectorstore_path)
        print(f"✅ Vector store salvo em: {vectorstore_path}")
        print(f"\nPronto para consultas semânticas!")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("🔄 Instalando dependências...")
        install_dependencies()
        print("🔁 Execute o script novamente após a instalação.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

def main():
    print("="*60)
    print("🔧 EXTRAÇÃO E EMBEDDING COM LANGCHAIN + DOCLING + HF")
    print("="*60)
    extract_and_embed()
    print("\n✅ Processo concluído!")
    print("Consulte o vector store para buscas semânticas.")

if __name__ == "__main__":
    main()
