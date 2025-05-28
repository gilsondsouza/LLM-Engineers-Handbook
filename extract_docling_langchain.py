#!/usr/bin/env python3
"""
Script para extrair PDFs usando Docling + LangChain
Combinação robusta para extração e processamento de documentos
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

def install_dependencies():
    """Instala as dependências necessárias"""
    dependencies = [
        "docling",
        "langchain",
        "langchain-community",
        "pypdf",
        "pdfplumber"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep} já instalado")
        except ImportError:
            print(f"📦 Instalando {dep}...")
            os.system(f"pip install {dep}")

def extract_with_docling_langchain():
    """Extrai PDFs usando Docling + LangChain"""
    
    print("🚀 Iniciando extração com Docling + LangChain...")
    
    try:
        # Importações após instalação
        from langchain_community.document_loaders import PyPDFLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain.schema import Document
        
        uploads_dir = Path("uploads")
        results = []
        all_documents = []
        
        # Configurar text splitter para chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        
        # Processar cada PDF
        for pdf_file in uploads_dir.glob("*.pdf"):
            print(f"\n📄 Processando: {pdf_file.name}")
            
            try:
                # Método 1: LangChain PyPDFLoader
                loader = PyPDFLoader(str(pdf_file))
                documents = loader.load()
                
                # Combinar todo o texto
                full_text = "\n".join([doc.page_content for doc in documents])
                
                # Criar chunks para RAG
                chunks = text_splitter.split_text(full_text)
                
                # Informações do documento
                doc_info = {
                    "filename": pdf_file.name,
                    "filepath": str(pdf_file),
                    "extracted_at": datetime.now().isoformat(),
                    "method": "langchain_pypdf",
                    "pages": len(documents),
                    "char_count": len(full_text),
                    "word_count": len(full_text.split()),
                    "chunk_count": len(chunks),
                    "text": full_text,
                    "chunks": chunks
                }
                
                results.append(doc_info)
                
                # Adicionar documentos à lista geral
                for i, doc in enumerate(documents):
                    doc.metadata.update({
                        "source_file": pdf_file.name,
                        "page_number": i + 1,
                        "extraction_method": "docling_langchain"
                    })
                    all_documents.append(doc)
                
                # Salvar texto completo
                text_output_file = f"data/extracted_texts/{pdf_file.stem}_langchain.txt"
                Path(text_output_file).parent.mkdir(parents=True, exist_ok=True)
                
                with open(text_output_file, 'w', encoding='utf-8') as f:
                    f.write(full_text)
                
                # Salvar chunks separados
                chunks_output_file = f"data/extracted_texts/{pdf_file.stem}_chunks.json"
                with open(chunks_output_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "filename": pdf_file.name,
                        "chunks": [{"chunk_id": i, "text": chunk} for i, chunk in enumerate(chunks)]
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"✅ {pdf_file.name} extraído com sucesso")
                print(f"   📊 Páginas: {len(documents)}")
                print(f"   📄 Caracteres: {len(full_text):,}")
                print(f"   📝 Palavras: {len(full_text.split()):,}")
                print(f"   🧩 Chunks: {len(chunks)}")
                print(f"   💾 Texto: {text_output_file}")
                print(f"   💾 Chunks: {chunks_output_file}")
                
                # Buscar termos específicos
                search_terms = ["JULIA CAROLINA BORGES", "JULIA", "CAROLINA", "BORGES"]
                for term in search_terms:
                    if term.upper() in full_text.upper():
                        print(f"🎯 ENCONTRADO: '{term}' no arquivo {pdf_file.name}!")
                        
                        # Encontrar contexto
                        lines = full_text.split('\n')
                        for i, line in enumerate(lines):
                            if term.upper() in line.upper():
                                print(f"   📍 Linha {i+1}: {line.strip()}")
                                break
                
            except Exception as e:
                print(f"❌ Erro ao processar {pdf_file.name}: {str(e)}")
                continue
        
        # Salvar resumo completo
        if results:
            summary_file = "data/artifacts/docling_langchain_summary.json"
            Path(summary_file).parent.mkdir(parents=True, exist_ok=True)
            
            summary_data = {
                "extraction_summary": {
                    "total_files": len(results),
                    "extraction_method": "docling_langchain",
                    "extracted_at": datetime.now().isoformat(),
                    "total_pages": sum(doc['pages'] for doc in results),
                    "total_characters": sum(doc['char_count'] for doc in results),
                    "total_words": sum(doc['word_count'] for doc in results),
                    "total_chunks": sum(doc['chunk_count'] for doc in results)
                },
                "files": results
            }
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 RESUMO DA EXTRAÇÃO DOCLING + LANGCHAIN:")
            print(f"   📄 Arquivos processados: {len(results)}")
            print(f"   📑 Total de páginas: {sum(doc['pages'] for doc in results)}")
            print(f"   📊 Total de caracteres: {sum(doc['char_count'] for doc in results):,}")
            print(f"   📝 Total de palavras: {sum(doc['word_count'] for doc in results):,}")
            print(f"   🧩 Total de chunks: {sum(doc['chunk_count'] for doc in results)}")
            print(f"   💾 Resumo salvo em: {summary_file}")
            
            return results, all_documents
        else:
            print("❌ Nenhum arquivo foi processado com sucesso")
            return [], []
            
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Instalando dependências...")
        install_dependencies()
        print("🔄 Execute o script novamente após a instalação")
        return [], []
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return [], []

def create_rag_pipeline(documents: List[Any]):
    """Cria pipeline RAG com os documentos extraídos"""
    
    if not documents:
        print("❌ Nenhum documento para criar pipeline RAG")
        return None
    
    try:
        from langchain.vectorstores import FAISS
        from langchain.embeddings import HuggingFaceEmbeddings
        from langchain.chains import RetrievalQA
        
        print(f"\n🧠 Criando pipeline RAG com {len(documents)} documentos...")
        
        # Configurar embeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Criar vector store
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        # Salvar vector store
        vectorstore_path = "data/vectorstore/docling_langchain"
        Path(vectorstore_path).parent.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(vectorstore_path)
        
        print(f"✅ Vector store criado e salvo em: {vectorstore_path}")
        
        # Criar retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        return retriever
        
    except ImportError as e:
        print(f"❌ Dependências para RAG não encontradas: {str(e)}")
        print("💡 Instale: pip install sentence-transformers faiss-cpu")
        return None
    except Exception as e:
        print(f"❌ Erro ao criar pipeline RAG: {str(e)}")
        return None

def search_documents(search_term: str = "JULIA CAROLINA BORGES"):
    """Busca avançada nos documentos extraídos"""
    
    print(f"\n🔍 BUSCA AVANÇADA POR: '{search_term}'")
    print("=" * 60)
    
    # Buscar no resumo
    summary_file = "data/artifacts/docling_langchain_summary.json"
    if Path(summary_file).exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary = json.load(f)
        
        found_in_files = []
        
        for file_data in summary.get('files', []):
            text = file_data.get('text', '')
            if search_term.upper() in text.upper():
                found_in_files.append(file_data['filename'])
                
                print(f"✅ ENCONTRADO em: {file_data['filename']}")
                print(f"   📊 Páginas: {file_data['pages']}")
                print(f"   📝 Palavras: {file_data['word_count']:,}")
                print(f"   🧩 Chunks: {file_data['chunk_count']}")
                
                # Mostrar contexto
                lines = text.split('\n')
                for i, line in enumerate(lines):
                    if search_term.upper() in line.upper():
                        print(f"   📍 Contexto encontrado:")
                        start = max(0, i-1)
                        end = min(len(lines), i+2)
                        for j in range(start, end):
                            prefix = ">>> " if j == i else "    "
                            print(f"   {prefix}{lines[j].strip()}")
                        print()
                        break
        
        if not found_in_files:
            print(f"❌ Termo '{search_term}' não encontrado nos documentos")
            
            # Buscar termos alternativos
            alt_terms = search_term.split()
            for term in alt_terms:
                if len(term) > 2:  # Ignorar termos muito curtos
                    for file_data in summary.get('files', []):
                        if term.upper() in file_data.get('text', '').upper():
                            print(f"💡 Termo alternativo '{term}' encontrado em: {file_data['filename']}")
                            break
        
        return found_in_files
    
    else:
        print(f"❌ Arquivo de resumo não encontrado: {summary_file}")
        return []

def main():
    """Função principal"""
    print("=" * 70)
    print("🔧 EXTRAÇÃO DE PDFs COM DOCLING + LANGCHAIN")
    print("=" * 70)
    
    # Verificar PDFs disponíveis
    uploads_dir = Path("uploads")
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado na pasta uploads/")
        return
    
    print(f"📂 Arquivos PDF encontrados: {len(pdf_files)}")
    for pdf in pdf_files:
        file_size = pdf.stat().st_size / 1024 / 1024  # MB
        print(f"   📄 {pdf.name} ({file_size:.1f} MB)")
    
    # Extrair documentos
    results, documents = extract_with_docling_langchain()
    
    if results:
        # Buscar por termos específicos
        search_documents("JULIA CAROLINA BORGES")
        
        # Criar pipeline RAG (opcional)
        print(f"\n🤔 Deseja criar pipeline RAG com os documentos extraídos?")
        print("   (Isso permitirá fazer perguntas sobre o conteúdo)")
        
        # Para este exemplo, vamos criar automaticamente
        retriever = create_rag_pipeline(documents)
        
        if retriever:
            print("\n✅ Pipeline RAG criado com sucesso!")
            print("🎯 Agora você pode fazer perguntas sobre o conteúdo dos PDFs")
    
    print("\n" + "=" * 70)
    print("✅ PROCESSO CONCLUÍDO!")
    print("📁 Arquivos gerados:")
    print("   📄 data/extracted_texts/ - Textos e chunks extraídos")
    print("   📋 data/artifacts/docling_langchain_summary.json - Resumo completo")
    print("   🧠 data/vectorstore/ - Vector store para RAG")
    print("=" * 70)

if __name__ == "__main__":
    main()
