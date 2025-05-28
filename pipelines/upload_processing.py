from zenml import pipeline

from steps.etl.get_or_create_user import get_or_create_user
from steps.etl.process_uploads import process_uploaded_files, list_upload_files


@pipeline
def upload_processing_pipeline(
    user_full_name: str,
    uploads_folder: str = "uploads",
    use_llm_processing: bool = True
):
    """
    Pipeline para processar arquivos carregados na pasta uploads
    
    Args:
        user_full_name: Nome completo do usuário (formato: "Nome Sobrenome")
        uploads_folder: Caminho para a pasta de uploads (padrão: "uploads")
        use_llm_processing: Se deve usar processamento LLM (padrão: True)
    """
    
    # Obtém ou cria o usuário
    user = get_or_create_user(user_full_name=user_full_name)
    
    # Lista arquivos disponíveis
    available_files = list_upload_files(uploads_folder=uploads_folder)
    
    # Processa os arquivos
    processed_files = process_uploaded_files(
        user=user,
        uploads_folder=uploads_folder,
        use_llm_processing=use_llm_processing
    )
    
    return processed_files


if __name__ == "__main__":
    # Exemplo de execução
    upload_processing_pipeline(
        user_full_name="Sistema Upload",
        uploads_folder="uploads"
    )
