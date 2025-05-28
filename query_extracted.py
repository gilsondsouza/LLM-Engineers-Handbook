#!/usr/bin/env python3
"""
Demo: Consultando o arquivo extraído usando LLM
"""

import json
from datetime import datetime
from pathlib import Path

class SimpleLLMQuery:
    """Sistema simples de consulta baseado no conteúdo extraído"""
    
    def __init__(self, chunks_file="data/artifacts/documento_chunks.json"):
        self.chunks = self.load_chunks(chunks_file)
        
    def load_chunks(self, chunks_file):
        """Carrega os chunks do arquivo processado"""
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Arquivo não encontrado: {chunks_file}")
            return []
    
    def search_content(self, query):
        """Busca conteúdo relevante baseado na consulta"""
        query_lower = query.lower()
        relevant_chunks = []
        
        for chunk in self.chunks:
            # Busca simples por palavras-chave
            title_lower = chunk['title'].lower()
            content_lower = chunk['content'].lower()
            
            score = 0
            
            # Pontuação baseada em palavras-chave
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in title_lower:
                    score += 3  # Título tem peso maior
                if keyword in content_lower:
                    score += 1
            
            if score > 0:
                chunk_result = chunk.copy()
                chunk_result['relevance_score'] = score
                relevant_chunks.append(chunk_result)
        
        # Ordenar por relevância
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_chunks
    
    def generate_response(self, query, max_chunks=3):
        """Gera resposta baseada nos chunks mais relevantes"""
        relevant_chunks = self.search_content(query)
        
        if not relevant_chunks:
            return "❌ Não encontrei informações relevantes para sua consulta."
        
        # Construir resposta
        response = f"📋 **Resposta para: {query}**\n\n"
        
        for i, chunk in enumerate(relevant_chunks[:max_chunks], 1):
            response += f"**{i}. {chunk['title']}** (Relevância: {chunk['relevance_score']})\n"
            response += f"{chunk['content']}\n\n"
        
        # Adicionar informações de contexto
        response += f"---\n"
        response += f"🔍 Consulta processada em: {datetime.now().strftime('%H:%M:%S')}\n"
        response += f"📊 Chunks analisados: {len(self.chunks)}\n"
        response += f"✅ Chunks relevantes: {len(relevant_chunks)}\n"
        
        return response

def demo_queries():
    """Demonstra consultas ao sistema"""
    
    print("🤖 DEMO: Consultando arquivo extraído com LLM")
    print("=" * 60)
    
    # Inicializar sistema de consulta
    llm_query = SimpleLLMQuery()
    
    if not llm_query.chunks:
        print("❌ Nenhum chunk encontrado. Execute primeiro o processo de extração.")
        return
    
    # Consultas de demonstração
    demo_questions = [
        "Quais tipos de arquivo são suportados?",
        "Como funciona o processamento?",
        "Quais tecnologias são utilizadas?",
        "Como fazer upload de arquivos?"
    ]
    
    for question in demo_questions:
        print(f"\n🔍 **CONSULTA:** {question}")
        print("-" * 50)
        
        response = llm_query.generate_response(question)
        print(response)
        
        print("=" * 60)

def interactive_mode():
    """Modo interativo para consultas"""
    
    print("\n🎯 MODO INTERATIVO")
    print("Digite suas perguntas sobre o documento extraído.")
    print("Digite 'sair' para encerrar.\n")
    
    llm_query = SimpleLLMQuery()
    
    if not llm_query.chunks:
        print("❌ Nenhum chunk encontrado.")
        return
    
    while True:
        try:
            query = input("❓ Sua pergunta: ").strip()
            
            if query.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
            
            if not query:
                continue
            
            print("\n🤖 Processando...")
            response = llm_query.generate_response(query)
            print(f"\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

def show_document_info():
    """Mostra informações sobre o documento carregado"""
    
    try:
        with open("data/artifacts/documento_chunks.json", 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print("📄 INFORMAÇÕES DO DOCUMENTO")
        print("=" * 40)
        print(f"📊 Total de seções: {len(chunks)}")
        print(f"🆔 ID do documento: {chunks[0]['document_id'] if chunks else 'N/A'}")
        
        total_words = sum(chunk['word_count'] for chunk in chunks)
        total_chars = sum(chunk['char_count'] for chunk in chunks)
        
        print(f"📝 Total de palavras: {total_words}")
        print(f"📄 Total de caracteres: {total_chars}")
        
        print("\n📚 SEÇÕES DISPONÍVEIS:")
        for i, chunk in enumerate(chunks, 1):
            print(f"   {i}. {chunk['title']} ({chunk['word_count']} palavras)")
        
    except FileNotFoundError:
        print("❌ Documento não encontrado. Execute primeiro a extração.")

def main():
    """Função principal"""
    
    print("🚀 LLM Query System - Arquivo Extraído")
    print("=" * 50)
    
    # Mostrar informações do documento
    show_document_info()
    
    print("\nEscolha uma opção:")
    print("1. 🎬 Demo com consultas pré-definidas")
    print("2. 🎯 Modo interativo")
    print("3. ❌ Sair")
    
    try:
        choice = input("\nSua escolha (1-3): ").strip()
        
        if choice == "1":
            demo_queries()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            print("👋 Até logo!")
        else:
            print("❌ Opção inválida")
            
    except KeyboardInterrupt:
        print("\n👋 Saindo...")

if __name__ == "__main__":
    main()
