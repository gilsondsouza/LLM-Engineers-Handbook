#!/usr/bin/env python3
"""
Script para processar dados extraídos e integrar com o pipeline LLM
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

def process_extracted_data(json_file="extracted_exemplo.json"):
    """Processa os dados extraídos para integração com o pipeline"""
    
    print("🔄 Processando dados extraídos...")
    
    try:
        # Carregar dados extraídos
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📄 Processando: {data['filename']}")
        
        # Criar estrutura de documento para o pipeline
        processed_document = {
            "id": f"doc_{data['filename']}_{int(datetime.now().timestamp())}",
            "type": "DocumentUpload",
            "source": "manual_upload",
            "filename": data['filename'],
            "content": {
                "raw_text": data['content'],
                "sections": data['sections'],
                "metadata": {
                    "file_size": data['file_size'],
                    "created_at": data['created_at'],
                    "modified_at": data['modified_at'],
                    "extraction_time": data['extraction_time'],
                    "statistics": {
                        "line_count": data['line_count'],
                        "word_count": data['word_count'],
                        "char_count": data['char_count'],
                        "section_count": len(data['sections'])
                    }
                }
            },
            "processing_timestamp": datetime.now().isoformat(),
            "status": "extracted"
        }
        
        # Criar chunks para processamento RAG
        chunks = []
        for i, section in enumerate(data['sections']):
            chunk = {
                "chunk_id": f"chunk_{processed_document['id']}_{i}",
                "document_id": processed_document['id'],
                "title": section['title'],
                "content": section['content'],
                "chunk_index": i,
                "word_count": len(section['content'].split()),
                "char_count": len(section['content'])
            }
            chunks.append(chunk)
        
        processed_document['chunks'] = chunks
        
        # Salvar documento processado
        output_file = "data/artifacts/processed_documento.json"
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_document, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Documento processado salvo em: {output_file}")
        
        # Criar arquivo de chunks separado
        chunks_file = "data/artifacts/documento_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Chunks salvos em: {chunks_file}")
        
        # Estatísticas do processamento
        print("\n📊 ESTATÍSTICAS DO PROCESSAMENTO:")
        print(f"   📄 Documento ID: {processed_document['id']}")
        print(f"   🧩 Total de chunks: {len(chunks)}")
        print(f"   📝 Palavras totais: {data['word_count']}")
        print(f"   📚 Seções: {len(data['sections'])}")
        
        return processed_document, chunks
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        return None, None

def create_rag_queries(document_data):
    """Cria consultas de exemplo para testar o sistema RAG"""
    
    queries = [
        "Quais tipos de arquivo são suportados pelo sistema de upload?",
        "Como funciona o processamento de arquivos?",
        "Quais tecnologias são utilizadas no sistema?",
        "Qual é o fluxo de trabalho do sistema de upload?",
        "Que tipos de documentos posso processar?",
        "Como o sistema indexa o conteúdo?",
        "Quais são as etapas do processamento?",
        "Que ferramentas são usadas para busca vetorial?"
    ]
    
    query_data = {
        "document_id": document_data['id'],
        "generated_queries": [
            {
                "query": query,
                "query_id": f"q_{i}_{int(datetime.now().timestamp())}",
                "expected_sections": ["Sobre o Sistema de Upload", "Como Funciona", "Tecnologias Utilizadas"]
            }
            for i, query in enumerate(queries)
        ],
        "created_at": datetime.now().isoformat()
    }
    
    # Salvar consultas
    queries_file = "data/artifacts/rag_queries.json"
    with open(queries_file, 'w', encoding='utf-8') as f:
        json.dump(query_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Consultas RAG salvas em: {queries_file}")
    
    return query_data

def main():
    """Função principal"""
    print("🚀 Iniciando processamento para pipeline LLM...")
    
    # Processar dados extraídos
    document, chunks = process_extracted_data()
    
    if document and chunks:
        print("\n✅ Dados processados com sucesso!")
        
        # Criar consultas de exemplo
        queries = create_rag_queries(document)
        
        print("\n🔄 PRÓXIMOS PASSOS:")
        print("1. ✅ Documento extraído e processado")
        print("2. ✅ Chunks criados para RAG")
        print("3. ✅ Consultas de exemplo geradas")
        print("4. 🔄 Execute o pipeline de feature engineering:")
        print("   python -m pipelines.feature_engineering")
        print("5. 🔄 Teste o sistema RAG com as consultas:")
        print("   python -m tools.rag")
        
        print("\n📁 ARQUIVOS GERADOS:")
        print("   📄 data/artifacts/processed_documento.json")
        print("   🧩 data/artifacts/documento_chunks.json")
        print("   ❓ data/artifacts/rag_queries.json")
        
    else:
        print("❌ Falha no processamento dos dados")

if __name__ == "__main__":
    main()
