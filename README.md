# Document Intelligence API

## Descrição

O **Document Intelligence API** é um projeto desenvolvido em Python com FastAPI, cujo objetivo é construir uma API para processamento e análise inteligente de documentos.

Atualmente, a aplicação oferece uma API REST para gerenciamento de documentos, com operações CRUD, upload de arquivos PDF com extração de texto, validação de dados e testes automatizados.

Nas próximas etapas, o projeto será expandido para incluir divisão de texto em chunks, embeddings, **Retrieval-Augmented Generation (RAG)** e integração com modelos de linguagem (LLMs), permitindo consultar informações presentes nos documentos.

O projeto também tem como objetivo aplicar boas práticas de engenharia de software, incluindo arquitetura modular, testes automatizados, gerenciamento de dependências, versionamento de código e integração contínua.

## Tecnologias utilizadas

- Python 3.13+
- FastAPI
- Pydantic
- Uvicorn
- PyMuPDF
- python-multipart
- pytest
- HTTPX2

## Funcionalidades implementadas

- Criação de documentos.
- Listagem de documentos.
- Consulta de documentos por ID.
- Atualização parcial de documentos.
- Exclusão de documentos.
- Upload de arquivos PDF.
- Extração de texto e contagem de páginas de PDFs.
- Validação de tipo, assinatura e tamanho dos arquivos enviados.
- Rejeição de PDFs corrompidos ou protegidos por senha.
- Limites de processamento para quantidade de páginas e tamanho do texto extraído.
- Validação e normalização dos dados recebidos.
- Tratamento de erros HTTP.
- Armazenamento temporário em memória.
- Testes automatizados.

## Estrutura do projeto

```text
app/
├── main.py                          # Criação da aplicação FastAPI
├── api/routes/
│   ├── documents.py                 # Endpoints de documentos e upload
│   └── health.py                    # Health check
├── schemas/
│   └── document.py                  # Schemas Pydantic
└── services/
    ├── document_service.py          # Regras de negócio e armazenamento em memória
    ├── pdf_service.py               # Validação e leitura do arquivo enviado
    └── pdf_extraction_service.py    # Extração de texto com PyMuPDF
tests/                               # Testes automatizados
```

## Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Git

### Configuração do ambiente

1. Clone o repositório:

   ```powershell
   git clone https://github.com/vitortbarboza/document-intelligence-api.git
   ```

2. Acesse o diretório do projeto:

   ```powershell
   cd document-intelligence-api
   ```

3. Crie o ambiente virtual:

   ```powershell
   python -m venv .venv
   ```

4. Ative o ambiente virtual no Windows:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

5. Instale o projeto e as dependências de desenvolvimento:

   ```powershell
   python -m pip install -e .
   python -m pip install --group dev
   ```

## Execução da API

Com o ambiente virtual ativado, execute o seguinte comando na raiz do projeto:

```powershell
python -m uvicorn app.main:app --reload
```

A API estará disponível nos seguintes endereços:

- **Health check:** http://127.0.0.1:8000/health
- **Documentação interativa (Swagger UI):** http://127.0.0.1:8000/docs

O endereço raiz (`/`) também redireciona para a documentação Swagger.

## Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/documents` | Criar um documento |
| POST | `/documents/upload` | Enviar um PDF e criar um documento com o texto extraído |
| GET | `/documents` | Listar todos os documentos |
| GET | `/documents/{document_id}` | Consultar um documento pelo ID |
| PATCH | `/documents/{document_id}` | Atualizar parcialmente um documento |
| DELETE | `/documents/{document_id}` | Excluir um documento |
| GET | `/health` | Verificar o funcionamento da API |

### Exemplo de criação de documento

**POST /documents**

Corpo da requisição:

```json
{
  "title": "Relatório Financeiro",
  "description": "Relatório anual de 2026"
}
```

Exemplo de resposta (`201 Created`):

```json
{
  "id": 1,
  "title": "Relatório Financeiro",
  "description": "Relatório anual de 2026"
}
```

### Exemplo de upload de PDF

**POST /documents/upload**

O arquivo é enviado como `multipart/form-data` no campo `file`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/documents/upload `
  -F "file=@relatorio.pdf;type=application/pdf"
```

Exemplo de resposta (`201 Created`):

```json
{
  "id": 2,
  "title": "relatorio.pdf",
  "description": "Document uploaded from PDF",
  "filename": "relatorio.pdf",
  "page_count": 3,
  "extracted_text": "Texto extraído da primeira página\n..."
}
```

Documentos criados por upload podem ser listados, consultados, atualizados e excluídos pelos mesmos endpoints CRUD. Os campos `filename`, `page_count` e `extracted_text` aparecem apenas nos documentos criados a partir de PDFs.

### Validação e tratamento de erros

A API utiliza Pydantic para validar e normalizar os dados recebidos.

As regras de validação são:

- `title`: obrigatório na criação, de 1 a 200 caracteres.
- `description`: obrigatório na criação, de 1 a 1000 caracteres.
- Espaços no início e no fim são removidos antes da validação de tamanho.
- Valores vazios ou contendo apenas espaços são rejeitados.
- Campos desconhecidos são rejeitados.
- No `PATCH`, os campos são opcionais, mas não aceitam `null`, e o corpo da requisição não pode ser vazio.

No upload de PDFs, as regras são:

- O tipo declarado do arquivo deve ser `application/pdf`.
- O conteúdo deve começar com a assinatura `%PDF-`.
- O arquivo pode ter no máximo 10 MiB.
- O PDF pode ter no máximo 500 páginas.
- O texto extraído pode ter no máximo 2.000.000 caracteres.
- PDFs corrompidos ou protegidos por senha são rejeitados.
- PDFs válidos sem texto extraível são aceitos, com `extracted_text` vazio.
- O nome do arquivo é normalizado antes de ser usado como título: caminhos são removidos, espaços extras são descartados, nomes longos são reduzidos a 200 caracteres (preservando a extensão) e nomes vazios recebem o valor `untitled.pdf`.

Os principais códigos HTTP utilizados são:

- `200`: operação realizada com sucesso.
- `201`: documento criado.
- `204`: documento excluído.
- `404`: documento não encontrado.
- `413`: arquivo maior que 10 MiB ou PDF acima dos limites de páginas ou de texto.
- `415`: tipo de arquivo não suportado.
- `422`: dados inválidos, assinatura de PDF inválida, PDF corrompido ou protegido por senha.

## Testes

O projeto utiliza **pytest** e o **TestClient do FastAPI** para executar testes automatizados.

Para executar todos os testes:

```powershell
python -m pytest -v
```

Os testes estão localizados no diretório `tests/`.

Os testes automatizados cobrem:

- Operações CRUD, validações de dados, tratamento de erros e normalização de textos.
- Upload de PDFs válidos, com uma ou várias páginas e sem texto extraível.
- Rejeição de tipos de arquivo inválidos, assinaturas inválidas e arquivos acima de 10 MiB.
- PDFs corrompidos, protegidos por senha e erros internos do PyMuPDF.
- Limites de páginas e de tamanho do texto extraído.
- Normalização de nomes de arquivos.
- Ciclo CRUD completo de documentos criados por upload.
- Isolamento entre testes, com o armazenamento e o contador de IDs reiniciados a cada teste.

## Limitações atuais

- Os documentos são armazenados em memória utilizando um dicionário Python, portanto os dados são perdidos quando a aplicação é reiniciada.
- Os arquivos PDF não são armazenados; apenas os metadados e o texto extraído são mantidos.
- Não há OCR: PDFs digitalizados (compostos apenas por imagens) resultam em texto vazio.
- O limite de 10 MiB é verificado pela aplicação depois que o corpo da requisição já foi recebido e armazenado temporariamente pelo servidor. Para bloquear requisições muito grandes antes disso, é necessário configurar um limite em um proxy reverso ou em um middleware.
- A extração de texto é executada de forma síncrona e pode bloquear outras requisições durante o processamento de PDFs grandes.
- A listagem de documentos retorna o texto extraído completo de cada PDF.

## Próximas etapas

- Adicionar persistência de dados.
- Implementar a divisão do texto extraído em chunks.
- Integrar embeddings e busca vetorial.
- Desenvolver um pipeline RAG.
- Explorar agentes de IA e LangGraph.
- Evoluir a infraestrutura de testes e integração contínua.
