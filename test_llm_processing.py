#!/usr/bin/env python
"""
Script de teste para demonstrar o processamento LLM dos arquivos de upload.
Este script irá processar os arquivos na pasta uploads usando LLM como primeiro passo.
"""

import os
from pathlib import Path
from llm_engineering.application.crawlers.file_upload import FileUploadCrawler
from llm_engineering.settings import settings


def main():
    """Função principal para teste do processamento LLM"""
    print("=== TESTE DE PROCESSAMENTO LLM ===")
    print(f"Modelo LLM configurado: {settings.OPENAI_MODEL_ID}")
    
    # Verifica se a chave da OpenAI está configurada
    if not settings.OPENAI_API_KEY:
        print("\n❌ ATENÇÃO: OPENAI_API_KEY não configurada!")
        print("Para processar com LLM, configure a chave da OpenAI:")
        print("  - Crie um arquivo .env no diretório raiz")
        print("  - Adicione: OPENAI_API_KEY=sua_chave_aqui")
        print("\nExecutando sem processamento LLM (apenas extração básica)...")
        use_llm = False
    else:
        print(f"✅ Chave OpenAI configurada: {settings.OPENAI_API_KEY[:10]}...")
        use_llm = True
    
    # Lista arquivos disponíveis
    uploads_path = Path("uploads")
    if not uploads_path.exists():
        print(f"\n❌ Pasta uploads não encontrada em: {uploads_path.absolute()}")
        return
    
    files = list(uploads_path.rglob("*.*"))
    print(f"\n📁 Arquivos encontrados na pasta uploads:")
    for i, file in enumerate(files, 1):
        print(f"  {i}. {file.name} ({file.suffix})")
    
    if not files:
        print("❌ Nenhum arquivo encontrado para processar")
        return
    
    # Inicializa o crawler
    crawler = FileUploadCrawler(
        uploads_folder="uploads",
        use_llm_processing=use_llm
    )
    
    print(f"\n🔄 Iniciando processamento...")
    print(f"  - Processamento LLM: {'✅ Ativado' if use_llm else '❌ Desativado'}")
    
    # Processa todos os arquivos
    try:
        processed_files = crawler.extract_all_uploads()
        
        print(f"\n✅ Processamento concluído!")
        print(f"  - Arquivos processados: {len(processed_files)}")
        
        if processed_files:
            print(f"\n📋 Arquivos processados:")
            for file in processed_files:
                print(f"  ✓ {Path(file).name}")
        
        if use_llm:
            print(f"\n🤖 Processamento LLM aplicado:")
            print(f"  - Extração de conteúdo estruturado")
            print(f"  - Geração de resumos")
            print(f"  - Identificação de tópicos principais")
            print(f"  - Extração de conceitos técnicos")
        else:
            print(f"\n📄 Processamento básico aplicado:")
            print(f"  - Extração de texto puro")
            print(f"  - Metadados básicos")
            
    except Exception as e:
        print(f"\n❌ Erro durante o processamento: {str(e)}")
        print(f"  - Verifique se as dependências estão instaladas")
        print(f"  - Verifique se a chave da OpenAI está configurada corretamente")


if __name__ == "__main__":
    main()
