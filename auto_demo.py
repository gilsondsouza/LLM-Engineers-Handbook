#!/usr/bin/env python3
"""
Auto Demo: Demonstra as consultas automaticamente
"""

import json
from datetime import datetime

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
            title_lower = chunk['title'].lower()
            content_lower = chunk['content'].lower()
            
            score = 0
            keywords = query_lower.split()
            for keyword in keywords:
                if keyword in title_lower:
                    score += 3
                if keyword in content_lower:
                    score += 1
            
            if score > 0:
                chunk_result = chunk.copy()
                chunk_result['relevance_score'] = score
                relevant_chunks.append(chunk_result)
        
        relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
        return relevant_chunks
    
    def generate_response(self, query, max_chunks=3):
        """Gera resposta baseada nos chunks mais relevantes"""
        relevant_chunks = self.search_content(query)
        
        if not relevant_chunks:
            return "❌ Não encontrei informações relevantes para sua consulta."
        
        response = f"📋 **Resposta para: {query}**\n\n"
        
        for i, chunk in enumerate(relevant_chunks[:max_chunks], 1):
            response += f"**{i}. {chunk['title']}** (Relevância: {chunk['relevance_score']})\n"
            response += f"{chunk['content']}\n\n"
        
        response += f"---\n"
        response += f"✅ Chunks relevantes encontrados: {len(relevant_chunks)}\n"
        
        return response

def main():
    """Demo automático"""
    
    print("🤖 AUTO DEMO: Consultando arquivo extraído com LLM")
    print("=" * 60)
    
    llm_query = SimpleLLMQuery()
    
    if not llm_query.chunks:
        print("❌ Nenhum chunk encontrado.")
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
    
    print("\n✅ DEMO CONCLUÍDO!")
    print("O arquivo foi extraído com sucesso e pode ser consultado usando LLM!")

if __name__ == "__main__":
    main()
