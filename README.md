
# Document Intelligence API

## Descrição

O **Document Intelligence API** é um projeto desenvolvido em Python com FastAPI, cujo objetivo é construir uma API para processamento e análise inteligente de documentos.

A aplicação permitirá extrair, organizar e consultar informações de documentos, utilizando técnicas de Inteligência Artificial, como **Retrieval-Augmented Generation (RAG)**, embeddings e modelos de linguagem (LLMs), para responder perguntas com base no conteúdo dos arquivos.

O projeto também tem como objetivo aplicar boas práticas de engenharia de software, incluindo arquitetura modular, testes automatizados, gerenciamento de dependências, versionamento de código e integração contínua.

## Instalação

### Pré-requisitos

- Python 3.13 ou superior
- Git

### Configuração do ambiente

1. Clone o repositório:

   ```powershell
   git clone <URL_DO_REPOSITORIO>
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

- **API:** http://127.0.0.1:8000
- **Health check:** http://127.0.0.1:8000/health
- **Documentação Swagger:** http://127.0.0.1:8000/docs

## Testes

O projeto utiliza **pytest** para executar testes automatizados.

Para executar todos os testes, utilize:

```powershell
python -m pytest -v
```

Os testes estão localizados no diretório `tests/`.
