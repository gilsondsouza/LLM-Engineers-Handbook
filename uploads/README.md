# 📁 Pasta Uploads

Esta pasta foi criada para receber arquivos que serão processados pelo sistema LLM Engineer's Handbook.

## 📋 Tipos de Arquivos Suportados

O sistema pode processar os seguintes tipos de arquivo:

### 📄 Documentos de Texto
- `.txt` - Arquivos de texto simples
- `.md` - Arquivos Markdown

### 📊 Documentos Estruturados  
- `.pdf` - Documentos PDF
- `.docx/.doc` - Documentos Microsoft Word
- `.pptx/.ppt` - Apresentações PowerPoint
- `.xlsx/.xls` - Planilhas Excel
- `.csv` - Arquivos CSV (dados tabulares)

### 💾 Dados
- `.json` - Arquivos JSON

## 🚀 Como Usar

### 1. Adicionar Arquivos
Simplesmente copie seus arquivos para esta pasta `uploads/`. Você pode criar subpastas se necessário.

### 2. Processar Arquivos

#### Opção A: Usando o script utilitário
```bash
# Processar todos os arquivos
python tools/process_uploads.py --all

# Processar arquivo específico
python tools/process_uploads.py --file "uploads/meu_documento.pdf"

# Listar arquivos disponíveis
python tools/process_uploads.py --list
```

#### Opção B: Usando o pipeline ZenML
```bash
# Executar pipeline completo
python tools/run.py --config configs/upload_processing.yaml --pipeline upload_processing
```

### 3. Verificar Processamento
Os arquivos processados serão:
- ✅ Extraído o conteúdo textual
- ✅ Salvos no banco de dados MongoDB
- ✅ Disponibilizados para o sistema RAG
- ✅ Indexados no banco vetorial Qdrant

## 📝 Exemplos de Uso

### Upload de Documentação
```bash
# Copie manuais, documentação técnica, etc.
cp documentacao_api.pdf uploads/
cp manual_usuario.docx uploads/docs/
```

### Upload de Dados
```bash
# Copie datasets, relatórios, etc.
cp relatorio_vendas.xlsx uploads/data/
cp dados_clientes.csv uploads/data/
```

### Upload de Conhecimento Base
```bash
# Copie artigos, papers, etc.
cp artigo_ml.pdf uploads/knowledge/
cp research_paper.pdf uploads/knowledge/
```

## 🔍 Metadados Extraídos

Para cada arquivo processado, o sistema extrai:

- **Título**: Nome do arquivo (sem extensão)
- **Conteúdo**: Texto extraído do arquivo
- **Tipo**: Tipo de arquivo (pdf, word, excel, etc.)
- **Tamanho**: Tamanho do arquivo em bytes
- **Páginas**: Número de páginas (para PDFs)
- **Linhas**: Número de linhas (para CSVs)

## ⚙️ Configurações Avançadas

### Processamento Customizado
Você pode modificar o `FileUploadCrawler` em:
`llm_engineering/application/crawlers/file_upload.py`

### Adicionar Novos Tipos
Para suportar novos tipos de arquivo, adicione processadores no método `supported_extensions`.

## 🛡️ Segurança

- ✅ Verificação de duplicatas (evita reprocessamento)
- ✅ Tratamento de erros robusto
- ✅ Logs detalhados de processamento
- ✅ Validação de tipos de arquivo

## 📊 Monitoramento

O processamento gera logs detalhados que podem ser encontrados nos outputs do ZenML ou nos logs da aplicação.

---

**💡 Dica**: Organize seus arquivos em subpastas temáticas para melhor organização:
```
uploads/
├── docs/           # Documentação
├── data/           # Datasets e planilhas  
├── knowledge/      # Base de conhecimento
└── temp/           # Arquivos temporários
```
