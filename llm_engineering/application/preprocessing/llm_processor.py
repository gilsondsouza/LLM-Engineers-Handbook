from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json

from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from jinja2 import Template

from llm_engineering.settings import settings


class BaseLLMProcessor(ABC):
    """Classe base para processadores LLM"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.OPENAI_MODEL_ID
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Inicializa o modelo LLM"""
        return ChatOpenAI(
            model=self.model_name,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1,  # Baixa criatividade para extração precisa
            max_tokens=4000
        )
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Retorna o prompt do sistema para o tipo de processamento"""
        pass
    
    @abstractmethod
    def get_user_prompt_template(self) -> str:
        """Retorna o template do prompt do usuário"""
        pass
    
    def process(self, content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa o conteúdo usando o LLM"""
        try:
            # Prepara os prompts
            system_prompt = self.get_system_prompt()
            user_template = Template(self.get_user_prompt_template())
            user_prompt = user_template.render(
                content=content,
                metadata=metadata or {}
            )
            
            # Faz a chamada para o LLM
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            logger.info(f"Processando conteúdo com LLM: {self.model_name}")
            response = self.llm.invoke(messages)
            
            # Processa a resposta
            return self._parse_response(response.content)
            
        except Exception as e:
            logger.error(f"Erro ao processar conteúdo com LLM: {str(e)}")
            return {
                "error": str(e),
                "original_content": content,
                "processed_content": content  # Fallback para conteúdo original
            }
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse da resposta do LLM"""
        try:
            # Tenta extrair JSON da resposta se houver
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_content = response[json_start:json_end].strip()
                return json.loads(json_content)
            
            # Se não for JSON, retorna como texto processado
            return {
                "processed_content": response.strip(),
                "processing_successful": True
            }
            
        except json.JSONDecodeError:
            logger.warning("Resposta do LLM não está em formato JSON válido")
            return {
                "processed_content": response.strip(),
                "processing_successful": True,
                "format_warning": "Resposta não está em JSON"
            }


class DocumentLLMProcessor(BaseLLMProcessor):
    """Processador LLM específico para documentos gerais"""
    
    def get_system_prompt(self) -> str:
        return """Você é um especialista em extração e estruturação de conteúdo de documentos.

Sua tarefa é analisar o conteúdo bruto extraído de um arquivo e convertê-lo em texto estruturado e limpo.

Objetivos:
1. Extrair e organizar as informações principais
2. Remover ruídos e formatação desnecessária
3. Manter a estrutura lógica do documento
4. Identificar seções, títulos e tópicos principais
5. Preservar informações importantes como tabelas, listas e dados

Retorne o resultado em formato JSON com a seguinte estrutura:
{
    "title": "Título principal do documento",
    "summary": "Resumo executivo do conteúdo",
    "main_content": "Conteúdo principal limpo e estruturado",
    "key_topics": ["tópico1", "tópico2", "tópico3"],
    "sections": [
        {
            "section_title": "Nome da seção",
            "content": "Conteúdo da seção"
        }
    ],
    "metadata": {
        "document_type": "tipo do documento",
        "language": "idioma detectado",
        "complexity": "alta/média/baixa"
    }
}"""
    
    def get_user_prompt_template(self) -> str:
        return """Analise o seguinte conteúdo extraído de um arquivo:

TIPO DE ARQUIVO: {{ metadata.get('file_type', 'desconhecido') }}
NOME DO ARQUIVO: {{ metadata.get('title', 'sem título') }}
TAMANHO: {{ metadata.get('file_size', 'desconhecido') }} bytes

CONTEÚDO BRUTO:
{{ content }}

Processe este conteúdo seguindo as instruções do sistema e retorne o resultado em formato JSON."""


class TechnicalDocumentLLMProcessor(BaseLLMProcessor):
    """Processador LLM específico para documentos técnicos"""
    
    def get_system_prompt(self) -> str:
        return """Você é um especialista em documentação técnica e análise de código.

Sua especialidade é processar documentos técnicos como:
- Documentação de APIs
- Manuais técnicos
- Código fonte
- Especificações técnicas
- Papers científicos

Objetivos específicos:
1. Identificar e extrair conceitos técnicos
2. Organizar códigos, exemplos e snippets
3. Extrair definições e termos técnicos
4. Identificar dependências e requisitos
5. Estruturar informações de forma hierárquica

Retorne o resultado em formato JSON:
{
    "title": "Título do documento técnico",
    "document_type": "api_doc|manual|code|specification|paper",
    "summary": "Resumo técnico",
    "main_content": "Conteúdo principal estruturado",
    "technical_concepts": ["conceito1", "conceito2"],
    "code_snippets": [
        {
            "language": "linguagem",
            "code": "código",
            "description": "descrição"
        }
    ],
    "requirements": ["requisito1", "requisito2"],
    "sections": [
        {
            "section_title": "Nome da seção",
            "content": "Conteúdo técnico da seção",
            "technical_level": "básico|intermediário|avançado"
        }
    ]
}"""
    
    def get_user_prompt_template(self) -> str:
        return """Analise este documento técnico:

ARQUIVO: {{ metadata.get('title', 'documento técnico') }}
TIPO: {{ metadata.get('file_type', 'desconhecido') }}

CONTEÚDO:
{{ content }}

Processe como documentação técnica seguindo as diretrizes do sistema."""


class DataDocumentLLMProcessor(BaseLLMProcessor):
    """Processador LLM específico para documentos de dados (CSV, Excel, etc.)"""
    
    def get_system_prompt(self) -> str:
        return """Você é um especialista em análise de dados e documentos estruturados.

Sua especialidade é processar arquivos de dados como:
- Planilhas Excel
- Arquivos CSV
- Relatórios de dados
- Datasets

Objetivos:
1. Identificar estrutura dos dados (colunas, tipos)
2. Analisar padrões e tendências
3. Extrair insights principais
4. Identificar qualidade dos dados
5. Sumarizar estatísticas relevantes

Formato de resposta JSON:
{
    "title": "Nome do dataset/planilha",
    "data_type": "csv|excel|report|dataset",
    "summary": "Resumo dos dados",
    "structure": {
        "columns": ["col1", "col2"],
        "row_count": "número estimado de linhas",
        "data_types": ["tipo1", "tipo2"]
    },
    "key_insights": ["insight1", "insight2"],
    "data_quality": {
        "completeness": "alta|média|baixa",
        "issues": ["problema1", "problema2"]
    },
    "main_content": "Descrição detalhada dos dados"
}"""
    
    def get_user_prompt_template(self) -> str:
        return """Analise este arquivo de dados:

ARQUIVO: {{ metadata.get('title', 'dados') }}
TIPO: {{ metadata.get('file_type', 'desconhecido') }}
LINHAS: {{ metadata.get('rows', 'desconhecido') }}

DADOS:
{{ content }}

Processe como arquivo de dados seguindo as diretrizes."""


class LLMProcessorFactory:
    """Factory para criar processadores LLM apropriados"""
    
    @staticmethod
    def create_processor(file_type: str, content: str = "") -> BaseLLMProcessor:
        """Cria o processador apropriado baseado no tipo de arquivo"""
        
        # Documentos técnicos
        technical_types = ['.py', '.js', '.java', '.cpp', '.md', '.rst']
        technical_keywords = ['api', 'documentation', 'manual', 'code', 'function', 'class']
        
        # Arquivos de dados
        data_types = ['.csv', '.xlsx', '.xls', '.json']
        
        if file_type in technical_types or any(keyword in content.lower() for keyword in technical_keywords):
            logger.info("Usando processador técnico")
            return TechnicalDocumentLLMProcessor()
        
        elif file_type in data_types:
            logger.info("Usando processador de dados")
            return DataDocumentLLMProcessor()
        
        else:
            logger.info("Usando processador de documentos gerais")
            return DocumentLLMProcessor()
