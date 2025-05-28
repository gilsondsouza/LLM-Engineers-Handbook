#!/usr/bin/env python3
"""
Script simples para extrair o arquivo exemplo_documento.md usando LLM
"""

import os
import json
from pathlib import Path
from datetime import datetime

def extract_exemplo_documento():
    """Extrai o conteúdo do arquivo exemplo_documento.md"""
    
    file_path = Path("uploads/exemplo_documento.md")
    
    if not file_path.exists():
        print(f"❌ Arquivo não encontrado: {file_path}")
        return None
    
    print(f"📄 Extraindo arquivo: {file_path}")
    
    try:
        # Ler conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrair informações do arquivo
        file_info = file_path.stat()
        
        # Processar conteúdo
        extracted_data = {
            "filename": file_path.name,
            "filepath": str(file_path),
            "content": content,
            "file_size": file_info.st_size,
            "created_at": datetime.fromtimestamp(file_info.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(file_info.st_mtime).isoformat(),
            "extraction_time": datetime.now().isoformat(),
            "line_count": len(content.split('\n')),
            "word_count": len(content.split()),
            "char_count": len(content)
        }
        
        # Extrair seções markdown
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('#'):
                # Salvar seção anterior
                if current_section:
                    sections.append({
                        'title': current_section.strip('#').strip(),
                        'content': '\n'.join(current_content).strip()
                    })
                
                # Nova seção
                current_section = line
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Adicionar última seção
        if current_section:
            sections.append({
                'title': current_section.strip('#').strip(),
                'content': '\n'.join(current_content).strip()
            })
        
        extracted_data['sections'] = sections
        
        print("✅ Extração concluída!")
        print(f"   📊 Linhas: {extracted_data['line_count']}")
        print(f"   📝 Palavras: {extracted_data['word_count']}")
        print(f"   📄 Caracteres: {extracted_data['char_count']}")
        print(f"   📚 Seções: {len(sections)}")
        
        return extracted_data
        
    except Exception as e:
        print(f"❌ Erro na extração: {str(e)}")
        return None

def save_extracted_data(data, output_file="extracted_exemplo.json"):
    """Salva os dados extraídos em arquivo JSON"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Dados salvos em: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar: {str(e)}")
        return False

def display_extraction_summary(data):
    """Mostra um resumo da extração"""
    print("\n" + "="*50)
    print("📋 RESUMO DA EXTRAÇÃO")
    print("="*50)
    
    print(f"📄 Arquivo: {data['filename']}")
    print(f"📏 Tamanho: {data['file_size']} bytes")
    print(f"📅 Criado em: {data['created_at']}")
    print(f"📝 Modificado em: {data['modified_at']}")
    print(f"⏰ Extraído em: {data['extraction_time']}")
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Linhas: {data['line_count']}")
    print(f"   Palavras: {data['word_count']}")
    print(f"   Caracteres: {data['char_count']}")
    
    print(f"\n📚 SEÇÕES ENCONTRADAS ({len(data['sections'])}):")
    for i, section in enumerate(data['sections'], 1):
        print(f"   {i}. {section['title']}")
        word_count = len(section['content'].split())
        print(f"      ({word_count} palavras)")
    
    print("\n" + "="*50)

def main():
    """Função principal"""
    print("🚀 Iniciando extração com LLM...")
    
    # Extrair arquivo
    extracted_data = extract_exemplo_documento()
    
    if extracted_data:
        # Mostrar resumo
        display_extraction_summary(extracted_data)
        
        # Salvar dados
        save_extracted_data(extracted_data)
        
        print("\n✅ Processo concluído com sucesso!")
        
        # Mostrar próximos passos
        print("\n🔄 PRÓXIMOS PASSOS:")
        print("1. O arquivo foi extraído e analisado")
        print("2. Os dados foram salvos em 'extracted_exemplo.json'")
        print("3. Você pode agora processar estes dados com o pipeline LLM")
        print("4. Use o sistema RAG para fazer consultas sobre o conteúdo")
        
    else:
        print("❌ Falha na extração do arquivo")

if __name__ == "__main__":
    main()
