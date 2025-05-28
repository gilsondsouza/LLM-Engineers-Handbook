#!/usr/bin/env python3
"""
Script para extrair PDFs usando Docling - Ferramenta de processamento de documentos da IBM
"""

import os
import json
from pathlib import Path
from datetime import datetime

def install_docling():
    """Instala o Docling se não estiver instalado"""
    try:
        import docling
        print("✅ Docling já está instalado")
        return True
    except ImportError:
        print("📦 Instalando Docling...")
        os.system("pip install docling")
        try:
            import docling
            print("✅ Docling instalado com sucesso")
            return True
        except ImportError:
            print("❌ Falha ao instalar Docling")
            return False

def extract_with_docling():
    """Extrai PDFs usando Docling"""
    
    if not install_docling():
        return
    
    try:
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        
        print("🚀 Iniciando extração com Docling...")
        
        # Inicializar o conversor
        converter = DocumentConverter()
        
        uploads_dir = Path("uploads")
        results = []
        
        # Processar todos os PDFs
        for pdf_file in uploads_dir.glob("*.pdf"):
            print(f"📄 Processando: {pdf_file.name}")
            
            try:
                # Converter PDF
                result = converter.convert(str(pdf_file))
                
                # Extrair texto
                text_content = result.document.export_to_markdown()
                
                # Informações do documento
                doc_info = {
                    "filename": pdf_file.name,
                    "filepath": str(pdf_file),
                    "extracted_at": datetime.now().isoformat(),
                    "char_count": len(text_content),
                    "word_count": len(text_content.split()),
                    "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 0,
                    "text": text_content
                }
                
                results.append(doc_info)
                
                # Salvar texto extraído individualmente
                text_output_file = f"data/extracted_texts/{pdf_file.stem}.txt"
                Path(text_output_file).parent.mkdir(parents=True, exist_ok=True)
                
                with open(text_output_file, 'w', encoding='utf-8') as f:
                    f.write(text_content)
                
                print(f"✅ {pdf_file.name} extraído com sucesso")
                print(f"   📊 Caracteres: {len(text_content)}")
                print(f"   📝 Palavras: {len(text_content.split())}")
                print(f"   💾 Salvo em: {text_output_file}")
                
                # Buscar por "JULIA CAROLINA BORGES"
                if "JULIA CAROLINA BORGES" in text_content.upper():
                    print(f"🎯 ENCONTRADO: 'JULIA CAROLINA BORGES' no arquivo {pdf_file.name}!")
                
            except Exception as e:
                print(f"❌ Erro ao processar {pdf_file.name}: {str(e)}")
                continue
        
        # Salvar resumo completo
        if results:
            summary_file = "data/artifacts/docling_extraction_summary.json"
            Path(summary_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n📋 RESUMO DA EXTRAÇÃO:")
            print(f"   📄 Arquivos processados: {len(results)}")
            print(f"   💾 Resumo salvo em: {summary_file}")
            
            # Estatísticas gerais
            total_chars = sum(doc['char_count'] for doc in results)
            total_words = sum(doc['word_count'] for doc in results)
            
            print(f"   📊 Total de caracteres: {total_chars:,}")
            print(f"   📝 Total de palavras: {total_words:,}")
            
            return results
        else:
            print("❌ Nenhum arquivo foi processado com sucesso")
            return []
            
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Certifique-se de que o Docling está instalado corretamente")
        return []
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return []

def search_in_extracted_content(search_term="JULIA CAROLINA BORGES"):
    """Busca um termo específico nos textos extraídos"""
    
    print(f"\n🔍 Buscando por: '{search_term}'")
    print("-" * 50)
    
    extracted_dir = Path("data/extracted_texts")
    found_files = []
    
    if not extracted_dir.exists():
        print("❌ Pasta de textos extraídos não encontrada")
        return found_files
    
    for text_file in extracted_dir.glob("*.txt"):
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if search_term.upper() in content.upper():
                found_files.append(text_file.name)
                print(f"✅ ENCONTRADO em: {text_file.name}")
                
                # Mostrar contexto ao redor do termo encontrado
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if search_term.upper() in line.upper():
                        start = max(0, i-2)
                        end = min(len(lines), i+3)
                        print(f"   📍 Contexto (linha {i+1}):")
                        for j in range(start, end):
                            prefix = ">>> " if j == i else "    "
                            print(f"   {prefix}{lines[j]}")
                        print()
                        break
            
        except Exception as e:
            print(f"❌ Erro ao ler {text_file.name}: {str(e)}")
    
    if not found_files:
        print(f"❌ Termo '{search_term}' não encontrado nos arquivos extraídos")
    
    return found_files

def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 EXTRAÇÃO DE PDFs COM DOCLING")
    print("=" * 60)
    
    # Verificar se há PDFs para processar
    uploads_dir = Path("uploads")
    pdf_files = list(uploads_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ Nenhum arquivo PDF encontrado na pasta uploads/")
        return
    
    print(f"📂 Arquivos PDF encontrados: {len(pdf_files)}")
    for pdf in pdf_files:
        print(f"   📄 {pdf.name}")
    
    # Extrair conteúdo
    results = extract_with_docling()
    
    # Buscar por "JULIA CAROLINA BORGES"
    if results:
        search_in_extracted_content("JULIA CAROLINA BORGES")
        
        # Buscar outros termos relevantes
        other_terms = ["JULIA", "CAROLINA", "BORGES"]
        for term in other_terms:
            found = search_in_extracted_content(term)
            if found:
                break
    
    print("\n✅ Processo concluído!")
    print("📁 Verifique os arquivos em:")
    print("   📄 data/extracted_texts/ - Textos individuais")
    print("   📋 data/artifacts/docling_extraction_summary.json - Resumo completo")

if __name__ == "__main__":
    main()
