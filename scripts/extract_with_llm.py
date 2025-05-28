#!/usr/bin/env python3
"""
Script para extrair e processar arquivos usando LLM
Parte do LLM Engineers Handbook
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
import markdown
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from llm_engineering.application.preprocessing.text_cleaning import TextCleaning
from llm_engineering.domain.documents import Document
from llm_engineering.infrastructure.files_io import FileHandler


class LLMFileExtractor:
    """Extrator de arquivos usando LLM para processamento inteligente"""
    
    def __init__(self, uploads_dir: str = "uploads"):
        self.uploads_dir = Path(uploads_dir)
        self.text_cleaner = TextCleaning()
        self.file_handler = FileHandler()
        
    def extract_markdown_content(self, file_path: Path) -> Dict[str, Any]:
        """Extrai conteúdo estruturado de arquivos Markdown"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Converter markdown para HTML para análise estrutural
            md = markdown.Markdown(extensions=['meta', 'toc'])
            html_content = md.convert(content)
            
            # Extrair metadados
            metadata = {
                'filename': file_path.name,
                'file_type': 'markdown',
                'size': file_path.stat().st_size,
                'created_at': datetime.fromtimestamp(file_path.stat().st_ctime),
                'modified_at': datetime.fromtimestamp(file_path.stat().st_mtime),
                'meta': getattr(md, 'Meta', {})
            }
            
            # Extrair seções
            sections = self._extract_sections(content)
            
            # Limpar e processar texto
            cleaned_text = self.text_cleaner.clean_text(content)
            
            return {
                'raw_content': content,
                'cleaned_content': cleaned_text,
                'html_content': html_content,
                'sections': sections,
                'metadata': metadata,
                'extraction_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Erro ao extrair {file_path}: {str(e)}")
            return None
    
    def _extract_sections(self, content: str) -> List[Dict[str, str]]:
        """Extrai seções do markdown baseado nos cabeçalhos"""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                # Salvar seção anterior se existir
                if current_section:
                    sections.append({
                        'title': current_section,
                        'content': '\n'.join(current_content).strip(),
                        'level': current_section.count('#')
                    })
                
                # Iniciar nova seção
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Adicionar última seção
        if current_section:
            sections.append({
                'title': current_section,
                'content': '\n'.join(current_content).strip(),
                'level': current_section.count('#')
            })
        
        return sections
    
    def create_document_object(self, extracted_data: Dict[str, Any]) -> Document:
        """Cria objeto Document para integração com o sistema"""
        try:
            return Document(
                id=f"doc_{extracted_data['metadata']['filename']}_{int(datetime.now().timestamp())}",
                content=extracted_data['cleaned_content'],
                metadata={
                    'filename': extracted_data['metadata']['filename'],
                    'file_type': extracted_data['metadata']['file_type'],
                    'sections': extracted_data['sections'],
                    'extraction_method': 'llm_extractor',
                    'size': extracted_data['metadata']['size'],
                    'created_at': extracted_data['metadata']['created_at'].isoformat(),
                    'modified_at': extracted_data['metadata']['modified_at'].isoformat()
                }
            )
        except Exception as e:
            print(f"Erro ao criar documento: {str(e)}")
            return None
    
    def extract_file(self, file_path: str) -> Dict[str, Any]:
        """Extrai um arquivo específico"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        print(f"Extraindo arquivo: {file_path}")
        
        if file_path.suffix.lower() == '.md':
            return self.extract_markdown_content(file_path)
        else:
            print(f"Tipo de arquivo não suportado ainda: {file_path.suffix}")
            return None
    
    def extract_all_uploads(self) -> List[Dict[str, Any]]:
        """Extrai todos os arquivos da pasta uploads"""
        if not self.uploads_dir.exists():
            print(f"Pasta uploads não encontrada: {self.uploads_dir}")
            return []
        
        extracted_files = []
        
        for file_path in self.uploads_dir.rglob('*'):
            if file_path.is_file():
                try:
                    extracted_data = self.extract_file(file_path)
                    if extracted_data:
                        extracted_files.append(extracted_data)
                        print(f"✓ Extraído: {file_path.name}")
                    else:
                        print(f"✗ Falha na extração: {file_path.name}")
                except Exception as e:
                    print(f"✗ Erro ao extrair {file_path.name}: {str(e)}")
        
        return extracted_files
    
    def save_extracted_data(self, extracted_data: List[Dict[str, Any]], output_file: str = "data/artifacts/extracted_documents.json"):
        """Salva os dados extraídos em arquivo JSON"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Converter datetime objects para string para serialização JSON
            serializable_data = []
            for data in extracted_data:
                serializable_item = json.loads(json.dumps(data, default=str))
                serializable_data.append(serializable_item)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Dados salvos em: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"✗ Erro ao salvar dados: {str(e)}")
            return None


def main():
    """Função principal do script"""
    print("=== LLM File Extractor ===")
    print("Extraindo arquivos da pasta uploads...")
    
    # Inicializar extrator
    extractor = LLMFileExtractor()
    
    # Extrair todos os arquivos
    extracted_data = extractor.extract_all_uploads()
    
    if extracted_data:
        print(f"\n✓ Total de arquivos extraídos: {len(extracted_data)}")
        
        # Salvar dados extraídos
        output_file = extractor.save_extracted_data(extracted_data)
        
        # Mostrar resumo
        print("\n=== Resumo da Extração ===")
        for data in extracted_data:
            metadata = data['metadata']
            print(f"📄 {metadata['filename']}")
            print(f"   Tipo: {metadata['file_type']}")
            print(f"   Tamanho: {metadata['size']} bytes")
            print(f"   Seções: {len(data['sections'])}")
            print()
        
        print("=== Extração Concluída ===")
    else:
        print("✗ Nenhum arquivo foi extraído.")


if __name__ == "__main__":
    main()
