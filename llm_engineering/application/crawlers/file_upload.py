import os
from pathlib import Path
from typing import Dict, Any, List
import mimetypes
import json

from loguru import logger
from langchain_community.document_loaders import (
    TextLoader, 
    PyPDFLoader, 
    CSVLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredPowerPointLoader,
    UnstructuredExcelLoader
)

from llm_engineering.domain.documents import ArticleDocument
from llm_engineering.settings import settings
from llm_engineering.application.preprocessing.llm_processor import LLMProcessorFactory

from .base import BaseCrawler


class FileUploadCrawler(BaseCrawler):
    """Crawler para processar arquivos carregados na pasta uploads"""
    
    model = ArticleDocument
    
    def __init__(self, uploads_folder: str = "uploads", use_llm_processing: bool = True) -> None:
        super().__init__()
        self.uploads_folder = uploads_folder
        self.use_llm_processing = use_llm_processing
        self.supported_extensions = {
            '.txt': self._process_text,
            '.md': self._process_text,
            '.pdf': self._process_pdf,
            '.csv': self._process_csv,
            '.docx': self._process_word,
            '.doc': self._process_word,
            '.pptx': self._process_powerpoint,
            '.ppt': self._process_powerpoint,
            '.xlsx': self._process_excel,
            '.xls': self._process_excel,
            '.json': self._process_json
        }
    
    def extract(self, file_path: str, **kwargs) -> None:
        """Extrai conteúdo de um arquivo específico"""
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return
        
        # Verifica se o arquivo já foi processado
        old_model = self.model.find(link=file_path)
        if old_model is not None:
            logger.info(f"Arquivo já processado: {file_path}")
            return
            
        logger.info(f"Iniciando processamento do arquivo: {file_path}")
          try:
            content = self._extract_content(file_path)
            if content:
                # Aplica processamento LLM se habilitado
                if self.use_llm_processing:
                    content = self._apply_llm_processing(file_path, content)
                
                self._save_document(file_path, content, **kwargs)
                logger.info(f"Arquivo processado com sucesso: {file_path}")
            else:
                logger.warning(f"Não foi possível extrair conteúdo do arquivo: {file_path}")
                
        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {str(e)}")
      def extract_all_uploads(self, **kwargs) -> List[str]:
        """Processa todos os arquivos da pasta uploads"""
        uploads_path = Path(self.uploads_folder)
        
        if not uploads_path.exists():
            logger.warning(f"Pasta uploads não encontrada: {uploads_path}")
            return []
        
        processed_files = []
        
        for file_path in uploads_path.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    self.extract(str(file_path), **kwargs)
                    processed_files.append(str(file_path))
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {str(e)}")
        
        logger.info(f"Processados {len(processed_files)} arquivos da pasta uploads")
        return processed_files
    
    def _apply_llm_processing(self, file_path: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica processamento LLM ao conteúdo extraído"""
        try:
            logger.info(f"Aplicando processamento LLM ao arquivo: {file_path}")
            
            # Obtém o tipo de arquivo
            file_extension = Path(file_path).suffix.lower()
            
            # Cria o processador apropriado
            processor = LLMProcessorFactory.create_processor(
                file_type=file_extension,
                content=content.get('content', '')
            )
            
            # Processa o conteúdo principal
            raw_content = content.get('content', '')
            if not raw_content:
                logger.warning("Conteúdo vazio para processamento LLM")
                return content
            
            # Aplica processamento LLM
            llm_result = processor.process(
                content=raw_content,
                metadata=content
            )
            
            # Combina resultado original com processamento LLM
            enhanced_content = {
                **content,  # Mantém dados originais
                'llm_processed': True,
                'llm_processing_successful': llm_result.get('processing_successful', False),
                'original_content': raw_content,  # Backup do conteúdo original
            }
            
            # Se o processamento LLM foi bem-sucedido, usa o conteúdo processado
            if llm_result.get('processing_successful', False):
                if 'processed_content' in llm_result:
                    enhanced_content['content'] = llm_result['processed_content']
                
                # Adiciona informações estruturadas se disponíveis
                if 'title' in llm_result and llm_result['title']:
                    enhanced_content['llm_title'] = llm_result['title']
                
                if 'summary' in llm_result:
                    enhanced_content['summary'] = llm_result['summary']
                
                if 'key_topics' in llm_result:
                    enhanced_content['key_topics'] = llm_result['key_topics']
                
                if 'sections' in llm_result:
                    enhanced_content['sections'] = llm_result['sections']
                
                if 'technical_concepts' in llm_result:
                    enhanced_content['technical_concepts'] = llm_result['technical_concepts']
                
                if 'metadata' in llm_result:
                    enhanced_content['llm_metadata'] = llm_result['metadata']
            
            else:
                logger.warning("Processamento LLM falhou, mantendo conteúdo original")
                enhanced_content['llm_error'] = llm_result.get('error', 'Processamento falhou')
            
            return enhanced_content
            
        except Exception as e:
            logger.error(f"Erro no processamento LLM para {file_path}: {str(e)}")
            # Retorna conteúdo original em caso de erro
            content['llm_processed'] = False
            content['llm_error'] = str(e)
            return content
    
    def _extract_content(self, file_path: str) -> Dict[str, Any]:
        """Extrai conteúdo baseado no tipo de arquivo"""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in self.supported_extensions:
            logger.warning(f"Tipo de arquivo não suportado: {file_extension}")
            return {}
        
        processor = self.supported_extensions[file_extension]
        return processor(file_path)
    
    def _process_text(self, file_path: str) -> Dict[str, Any]:
        """Processa arquivos de texto (.txt, .md)"""
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents = loader.load()
            
            if documents:
                return {
                    "title": Path(file_path).stem,
                    "content": documents[0].page_content,
                    "file_type": "text",
                    "file_size": os.path.getsize(file_path)
                }
        except Exception as e:
            logger.error(f"Erro ao processar arquivo de texto {file_path}: {str(e)}")
        
        return {}
    
    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Processa arquivos PDF"""
        try:
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            content = "\n".join([doc.page_content for doc in documents])
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "pdf",
                "pages": len(documents),
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar PDF {file_path}: {str(e)}")
        
        return {}
    
    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """Processa arquivos CSV"""
        try:
            loader = CSVLoader(file_path)
            documents = loader.load()
            
            content = "\n".join([doc.page_content for doc in documents])
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "csv",
                "rows": len(documents),
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar CSV {file_path}: {str(e)}")
        
        return {}
    
    def _process_word(self, file_path: str) -> Dict[str, Any]:
        """Processa documentos Word (.docx, .doc)"""
        try:
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
            
            content = "\n".join([doc.page_content for doc in documents])
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "word",
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar documento Word {file_path}: {str(e)}")
        
        return {}
    
    def _process_powerpoint(self, file_path: str) -> Dict[str, Any]:
        """Processa apresentações PowerPoint (.pptx, .ppt)"""
        try:
            loader = UnstructuredPowerPointLoader(file_path)
            documents = loader.load()
            
            content = "\n".join([doc.page_content for doc in documents])
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "powerpoint",
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar PowerPoint {file_path}: {str(e)}")
        
        return {}
    
    def _process_excel(self, file_path: str) -> Dict[str, Any]:
        """Processa planilhas Excel (.xlsx, .xls)"""
        try:
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
            
            content = "\n".join([doc.page_content for doc in documents])
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "excel",
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar Excel {file_path}: {str(e)}")
        
        return {}
    
    def _process_json(self, file_path: str) -> Dict[str, Any]:
        """Processa arquivos JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Converte JSON para texto legível
            content = json.dumps(data, indent=2, ensure_ascii=False)
            
            return {
                "title": Path(file_path).stem,
                "content": content,
                "file_type": "json",
                "file_size": os.path.getsize(file_path)
            }
        except Exception as e:
            logger.error(f"Erro ao processar JSON {file_path}: {str(e)}")
        
        return {}
    
    def _save_document(self, file_path: str, content: Dict[str, Any], **kwargs) -> None:
        """Salva o documento processado no banco de dados"""
        user = kwargs.get("user")
        if not user:
            logger.error("Usuário não fornecido para salvar documento")
            return
        
        instance = self.model(
            content=content,
            link=file_path,
            platform="file_upload",
            author_id=user.id,
            author_full_name=user.full_name,
        )
        instance.save()
        
        logger.info(f"Documento salvo: {file_path}")
