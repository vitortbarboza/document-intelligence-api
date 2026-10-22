# Document Intelligence API

## Descrição

O **Document Intelligence API** é um projeto desenvolvido em Python com FastAPI, cujo objetivo é construir uma API para processamento e análise inteligente de documentos.

Atualmente, a aplicação oferece uma API REST para gerenciamento de documentos, com operações CRUD, validação de dados e testes automatizados.

Nas próximas etapas, o projeto será expandido para incluir processamento de arquivos PDF, embeddings, **Retrieval-Augmented Generation (RAG)** e integração com modelos de linguagem (LLMs), permitindo consultar informações presentes nos documentos.

O projeto também tem como objetivo aplicar boas práticas de engenharia de software, incluindo arquitetura modular, testes automatizados, gerenciamento de dependências, versionamento de código e integração contínua.

## Tecnologias utilizadas

- Python 3.13+
- FastAPI
- Pydantic
- Uvicorn
- pytest
- HTTPX

## Funcionalidades implementadas

- Criação de documentos.
- Listagem de documentos.
- Consulta de documentos por ID.
- Atualização parcial de documentos.
- Exclusão de documentos.
- Validação e normalização dos dados recebidos.
- Tratamento de erros HTTP.
- Armazenamento temporário em memória.
- Testes automatizados.

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

### Validação e tratamento de erros

A API utiliza Pydantic para validar e normalizar os dados recebidos.

As regras de validação são:

- `title`: obrigatório na criação, de 1 a 200 caracteres.
- `description`: obrigatório na criação, de 1 a 1000 caracteres.
- Espaços no início e no fim são removidos antes da validação de tamanho.
- Valores vazios ou contendo apenas espaços são rejeitados.
- Campos desconhecidos são rejeitados.
- No `PATCH`, os campos são opcionais, mas não aceitam `null`, e o corpo da requisição não pode ser vazio.

Os principais códigos HTTP utilizados são:

- `200`: operação realizada com sucesso.
- `201`: documento criado.
- `204`: documento excluído.
- `404`: documento não encontrado.
- `422`: dados inválidos.

## Testes

O projeto utiliza **pytest** e o **TestClient do FastAPI** para executar testes automatizados.

Para executar todos os testes:

```powershell
python -m pytest -v
```

Os testes estão localizados no diretório `tests/`.

Os testes automatizados cobrem operações CRUD, validações de dados, tratamento de erros, normalização de textos e isolamento entre testes.

## Limitações atuais

Os documentos são armazenados em memória utilizando um dicionário Python.

Isso significa que os dados são perdidos quando a aplicação é reiniciada.

Nesta etapa, a API gerencia apenas metadados textuais dos documentos (`title` e `description`). Ainda não realiza upload ou processamento de arquivos.

## Próximas etapas

- Implementar upload e processamento de arquivos PDF.
- Adicionar persistência de dados.
- Implementar extração e divisão de texto em chunks.
- Integrar embeddings e busca vetorial.
- Desenvolver um pipeline RAG.
- Explorar agentes de IA e LangGraph.
- Evoluir a infraestrutura de testes e integração contínua.