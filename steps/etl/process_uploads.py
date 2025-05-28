from pathlib import Path
from typing import List

from loguru import logger
from typing_extensions import Annotated
from zenml import get_step_context, step

from llm_engineering.application.crawlers.file_upload import FileUploadCrawler
from llm_engineering.domain.documents import UserDocument


@step
def process_uploaded_files(
    user: UserDocument, 
    uploads_folder: str = "uploads",
    use_llm_processing: bool = True
) -> Annotated[List[str], "processed_files"]:
    """
    Step ZenML para processar arquivos carregados na pasta uploads
    
    Args:
        user: Usuário responsável pelos arquivos
        uploads_folder: Caminho para a pasta de uploads
        use_llm_processing: Se deve usar processamento LLM
        
    Returns:
        Lista de arquivos processados com sucesso
    """
    
    processing_mode = "com LLM" if use_llm_processing else "básico"
    logger.info(f"Iniciando processamento {processing_mode} de arquivos na pasta: {uploads_folder}")
    
    # Verifica se a pasta existe
    uploads_path = Path(uploads_folder)
    if not uploads_path.exists():
        logger.warning(f"Pasta uploads não encontrada: {uploads_path}")
        return []
    
    # Inicializa o crawler
    crawler = FileUploadCrawler(
        uploads_folder=uploads_folder,
        use_llm_processing=use_llm_processing
    )
    
    # Processa todos os arquivos
    processed_files = crawler.extract_all_uploads(user=user)
    
    # Prepara metadados para o step
    metadata = {
        "total_files_processed": len(processed_files),
        "uploads_folder": uploads_folder,
        "user_name": user.full_name,
        "llm_processing_enabled": use_llm_processing,
        "processing_mode": processing_mode
    }
    
    # Adiciona estatísticas por tipo de arquivo
    file_types = {}
    for file_path in processed_files:
        extension = Path(file_path).suffix.lower()
        file_types[extension] = file_types.get(extension, 0) + 1
    
    metadata["file_types_processed"] = file_types
    
    # Adiciona metadados ao contexto do step
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="processed_files", metadata=metadata)
    
    logger.info(f"Processamento concluído. {len(processed_files)} arquivos processados com sucesso")
    
    return processed_files


@step 
def list_upload_files(uploads_folder: str = "uploads") -> Annotated[List[str], "available_files"]:
    """
    Step para listar arquivos disponíveis na pasta uploads
    
    Args:
        uploads_folder: Caminho para a pasta de uploads
        
    Returns:
        Lista de arquivos disponíveis
    """
    
    uploads_path = Path(uploads_folder)
    
    if not uploads_path.exists():
        logger.warning(f"Pasta uploads não encontrada: {uploads_path}")
        return []
    
    available_files = []
    crawler = FileUploadCrawler(uploads_folder=uploads_folder)
    
    for file_path in uploads_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in crawler.supported_extensions:
            available_files.append(str(file_path))
    
    # Metadados
    metadata = {
        "total_files_found": len(available_files),
        "uploads_folder": uploads_folder,
        "supported_extensions": list(crawler.supported_extensions.keys())
    }
    
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="available_files", metadata=metadata)
    
    logger.info(f"Encontrados {len(available_files)} arquivos suportados na pasta uploads")
    
    return available_files
