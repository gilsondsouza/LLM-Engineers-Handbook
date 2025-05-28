#!/usr/bin/env python3
"""
Script para processar arquivos da pasta uploads
Uso: python tools/process_uploads.py
"""

import sys
from pathlib import Path
from typing import List

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from loguru import logger
from llm_engineering.application.crawlers.file_upload import FileUploadCrawler
from llm_engineering.domain.documents import UserDocument


def get_default_user() -> UserDocument:
    """Retorna um usuário padrão para processamento de arquivos"""
    # Tenta encontrar um usuário existente no banco
    existing_users = UserDocument.find_all()
    if existing_users:
        return existing_users[0]
    
    # Cria um usuário padrão se não existir
    user = UserDocument(
        first_name="Sistema",
        last_name="Upload"
    )
    user.save()
    return user


def process_single_file(file_path: str, use_llm: bool = True) -> bool:
    """Processa um único arquivo"""
    try:
        user = get_default_user()
        crawler = FileUploadCrawler(use_llm_processing=use_llm)
        crawler.extract(file_path, user=user)
        return True
    except Exception as e:
        logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
        return False


def process_all_uploads(use_llm: bool = True) -> List[str]:
    """Processa todos os arquivos da pasta uploads"""
    try:
        user = get_default_user()
        crawler = FileUploadCrawler(use_llm_processing=use_llm)
        processed_files = crawler.extract_all_uploads(user=user)
        return processed_files
    except Exception as e:
        logger.error(f"Erro ao processar pasta uploads: {str(e)}")
        return []


def list_uploaded_files() -> List[str]:
    """Lista todos os arquivos na pasta uploads"""
    uploads_path = Path("uploads")
    
    if not uploads_path.exists():
        logger.warning("Pasta uploads não encontrada")
        return []
    
    files = []
    for file_path in uploads_path.rglob("*"):
        if file_path.is_file():
            files.append(str(file_path))
    
    return files


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Processa arquivos da pasta uploads")
    parser.add_argument(
        "--file", 
        type=str, 
        help="Caminho para um arquivo específico para processar"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="Lista todos os arquivos na pasta uploads"
    )    parser.add_argument(
        "--all", 
        action="store_true", 
        help="Processa todos os arquivos da pasta uploads"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Desabilita o processamento LLM (usa apenas extração básica)"
    )
      args = parser.parse_args()
    
    # Determina se deve usar LLM
    use_llm = not args.no_llm
    
    if use_llm:
        logger.info("🤖 Processamento LLM HABILITADO - Conteúdo será processado e melhorado pelo LLM")
    else:
        logger.info("📄 Processamento LLM DESABILITADO - Apenas extração básica de texto")
    
    if args.list:
        files = list_uploaded_files()
        if files:
            logger.info(f"Encontrados {len(files)} arquivos na pasta uploads:")
            for file in files:
                print(f"  - {file}")
        else:
            logger.info("Nenhum arquivo encontrado na pasta uploads")
      elif args.file:
        logger.info(f"Processando arquivo: {args.file}")
        success = process_single_file(args.file, use_llm=use_llm)
        if success:
            logger.info("Arquivo processado com sucesso!")
        else:
            logger.error("Falha ao processar arquivo")
    
    elif args.all:
        logger.info("Processando todos os arquivos da pasta uploads...")
        processed_files = process_all_uploads(use_llm=use_llm)
        logger.info(f"Processados {len(processed_files)} arquivos com sucesso")
        
        if processed_files:
            logger.info("Arquivos processados:")
            for file in processed_files:
                print(f"  ✓ {file}")
    
    else:
        # Comportamento padrão: processar todos os arquivos
        logger.info("Processando todos os arquivos da pasta uploads...")
        processed_files = process_all_uploads(use_llm=use_llm)
        logger.info(f"Processados {len(processed_files)} arquivos com sucesso")


if __name__ == "__main__":
    main()
