# Document Intelligence API

## Descrição

O **Document Intelligence API** é um projeto desenvolvido em Python com FastAPI, cujo objetivo é construir uma API para processamento e análise inteligente de documentos.

Atualmente, a aplicação oferece uma API REST para gerenciamento de documentos, com operações CRUD, upload de arquivos PDF com extração de texto, persistência em banco de dados SQLite, migrações versionadas, validação de dados e testes automatizados.

Nas próximas etapas, o projeto será expandido para incluir divisão de texto em chunks, embeddings, **Retrieval-Augmented Generation (RAG)** e integração com modelos de linguagem (LLMs), permitindo consultar informações presentes nos documentos.

O projeto também tem como objetivo aplicar boas práticas de engenharia de software, incluindo arquitetura modular, testes automatizados, gerenciamento de dependências, versionamento de código e integração contínua.

## Tecnologias utilizadas

- Python 3.13+
- FastAPI
- Pydantic
- Uvicorn
- SQLAlchemy (ORM)
- SQLite
- Alembic
- PyMuPDF
- python-multipart
- pytest, pytest-cov e HTTPX2
- uv (gerenciamento de dependências e lockfile)
- Ruff (lint e formatação)
- Docker e Docker Compose
- GitHub Actions (integração contínua)

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
- Persistência dos documentos em banco de dados SQLite.
- Migrações de banco de dados versionadas com Alembic.
- Testes automatizados.

## Estrutura do projeto

```text
app/
├── main.py                          # Criação da aplicação FastAPI
├── api/routes/
│   ├── documents.py                 # Endpoints de documentos e upload
│   └── health.py                    # Health check
├── db/
│   └── database.py                  # Engine, sessões e dependência get_db
├── models/
│   └── document.py                  # Modelo ORM da tabela documents
├── repositories/
│   └── document_repository.py       # Operações de banco de dados (CRUD)
├── schemas/
│   └── document.py                  # Schemas Pydantic
└── services/
    ├── document_service.py          # Regras de negócio dos documentos
    ├── pdf_service.py               # Validação e leitura do arquivo enviado
    └── pdf_extraction_service.py    # Extração de texto com PyMuPDF
alembic/
└── versions/                        # Migrações do banco de dados
alembic.ini                          # Configuração do Alembic
tests/                               # Testes automatizados
scripts/
└── docker-smoke-test.sh             # Teste de inicialização do contêiner
.github/workflows/ci.yml             # Pipeline de integração contínua
pyproject.toml                       # Metadados, dependências e ferramentas
uv.lock                              # Versões exatas de todas as dependências
.python-version                      # Versão do Python usada pelo uv e pela CI
Dockerfile                           # Imagem da aplicação
compose.yaml                         # Execução com Docker Compose
```

As requisições seguem o fluxo **rotas → services → repositório → banco de dados**. Os services convertem os objetos ORM em schemas Pydantic, de modo que as rotas não manipulam diretamente os modelos do banco.

## Instalação

### Pré-requisitos

- Python 3.13 ou superior
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Git
- Docker (opcional, para execução em contêiner)

### Configuração do ambiente

1. Clone o repositório:

   ```powershell
   git clone https://github.com/vitortbarboza/document-intelligence-api.git
   ```

2. Acesse o diretório do projeto:

   ```powershell
   cd document-intelligence-api
   ```

3. Crie o ambiente virtual e instale o projeto com as dependências de desenvolvimento, nas versões exatas do `uv.lock`:

   ```powershell
   uv sync --locked
   ```

   O comando cria o diretório `.venv`, se necessário, e remove dele pacotes que não estejam declarados no projeto. A opção `--locked` falha se o `uv.lock` estiver desatualizado em relação ao `pyproject.toml`, em vez de alterá-lo silenciosamente.

4. Crie o banco de dados aplicando as migrações:

   ```powershell
   uv run alembic upgrade head
   ```

   Esse passo é obrigatório antes da primeira execução da API e sempre que novas migrações forem adicionadas. Sem ele, a tabela `documents` não existe e as requisições retornam erro `500`.

Os comandos deste documento usam `uv run`, que executa o comando no ambiente virtual do projeto. Alternativamente, ative o ambiente (`.\.venv\Scripts\Activate.ps1` no Windows) e execute os comandos diretamente, por exemplo `python -m alembic upgrade head`.

### Gerenciamento de dependências

As dependências são declaradas no `pyproject.toml`: as de execução em `[project].dependencies` e as de desenvolvimento (pytest, pytest-cov, HTTPX2 e Ruff) no grupo `dev` de `[dependency-groups]`. O arquivo `uv.lock` registra a versão exata de cada pacote e é utilizado no ambiente local, na CI e na imagem Docker, garantindo as mesmas versões em todos eles.

| Comando | Descrição |
|---|---|
| `uv add <pacote>` | Adiciona uma dependência de execução e atualiza o `uv.lock` |
| `uv add --group dev <pacote>` | Adiciona uma dependência de desenvolvimento |
| `uv lock --upgrade-package <pacote>` | Atualiza um pacote para a versão mais recente permitida |
| `uv lock --upgrade` | Atualiza todas as dependências dentro dos limites declarados |

Sempre faça commit do `pyproject.toml` e do `uv.lock` juntos.

## Execução da API

Com as migrações aplicadas, execute o seguinte comando na raiz do projeto:

```powershell
uv run uvicorn app.main:app --reload
```

A API estará disponível nos seguintes endereços:

- **Health check:** http://127.0.0.1:8000/health
- **Documentação interativa (Swagger UI):** http://127.0.0.1:8000/docs

O endereço raiz (`/`) também redireciona para a documentação Swagger.

## Banco de dados e migrações

Os documentos são armazenados em um banco SQLite. Por padrão, o arquivo `documents.db` fica na raiz do projeto, independentemente do diretório a partir do qual a API ou o Alembic são executados.

Para utilizar outro arquivo, defina a variável de ambiente `DATABASE_URL` antes de executar a API e o Alembic:

```powershell
$env:DATABASE_URL = "sqlite:///C:/caminho/para/outro.db"
```

Os arquivos de banco (`*.db`) são ignorados pelo Git.

Os IDs são gerados pelo banco com `AUTOINCREMENT`, portanto o ID de um documento excluído nunca é reutilizado.

### Comandos úteis do Alembic

| Comando | Descrição |
|---|---|
| `python -m alembic upgrade head` | Aplica todas as migrações pendentes |
| `python -m alembic current` | Mostra a revisão atual do banco |
| `python -m alembic history` | Lista as migrações existentes |
| `python -m alembic downgrade -1` | Reverte a última migração |
| `python -m alembic check` | Verifica se os modelos e as migrações estão sincronizados |
| `python -m alembic revision --autogenerate -m "descricao"` | Gera uma nova migração a partir das mudanças nos modelos |

Também é possível executar um comando em outro banco sem alterar a variável de ambiente:

```powershell
python -m alembic -x db_url=sqlite:///C:/caminho/para/outro.db upgrade head
```

Como o SQLite não suporta a maioria das alterações de tabela (`ALTER TABLE`), o Alembic está configurado com `render_as_batch=True`. Assim, as migrações geradas recriam a tabela quando necessário.

Antes de aplicar migrações em um banco com dados importantes, recomenda-se fazer uma cópia do arquivo `.db`. Migrações geradas automaticamente devem sempre ser revisadas antes de serem aplicadas.

## Execução com Docker

A imagem usa `python:3.13-slim` e instala apenas as dependências de execução, nas versões do `uv.lock`. Ao iniciar, o contêiner aplica as migrações (`alembic upgrade head`) e depois inicia o Uvicorn na porta `8000`.

Características da imagem:

- A aplicação é executada por um usuário sem privilégios (`app`, UID `10001`), e não como `root`.
- O banco SQLite fica em `/data/documents.db` (variável `DATABASE_URL`). O diretório `/data` deve ser montado em um volume para que os dados sobrevivam à recriação do contêiner.
- Um `HEALTHCHECK` consulta `/health` periodicamente; o estado aparece em `docker ps` e `docker compose ps`.
- As dependências ficam em uma camada separada do código, então alterações no código não reinstalam as dependências.

### Docker Compose (recomendado)

```powershell
docker compose up -d --build
```

| Comando | Descrição |
|---|---|
| `docker compose ps` | Mostra o estado do contêiner, incluindo o health check |
| `docker compose logs api` | Exibe os logs das migrações e da API |
| `docker compose down` | Para e remove o contêiner, preservando o volume |

O Compose:

- Publica a API apenas em `127.0.0.1:8000`, pois ela ainda não possui autenticação.
- Usa o volume nomeado `document-intelligence-data`, criado automaticamente na primeira execução. Se o volume já existir, ele é reutilizado; nesse caso, o Compose pode avisar que o volume não foi criado por ele, o que pode ser ignorado.
- Reinicia o contêiner automaticamente (`restart: unless-stopped`), exceto quando ele é parado manualmente.

> **Atenção:** `docker compose down -v` remove o volume e apaga o banco de dados.

### Docker sem Compose

```powershell
docker build -t document-intelligence-api:0.1.0 .
docker run -d --name document-intelligence-api `
  -p 127.0.0.1:8000:8000 `
  -v document-intelligence-data:/data `
  document-intelligence-api:0.1.0
```

### Volumes criados por versões anteriores da imagem

Versões anteriores da imagem executavam a aplicação como `root`; por isso, os arquivos dos volumes criados por elas pertencem ao `root`. Com a imagem atual, a API inicia e permite leituras, mas qualquer escrita falha com o erro `attempt to write a readonly database` (HTTP `500`).

Para corrigir, execute uma única vez, com o contêiner parado:

```powershell
# 1. Pare a API.
docker compose down

# 2. Faça um backup do volume em um arquivo .tar no diretório atual.
docker run --rm `
  -v document-intelligence-data:/data:ro `
  -v "${PWD}:/backup" `
  python:3.13-slim tar -cf /backup/document-intelligence-data-backup.tar -C /data .

# 3. Transfira a propriedade dos arquivos para o usuário da aplicação.
docker run --rm `
  -v document-intelligence-data:/data `
  python:3.13-slim chown -R 10001:10001 /data

# 4. Inicie a API novamente.
docker compose up -d --build
```

O passo 3 altera apenas o dono dos arquivos, não o seu conteúdo. Volumes novos não precisam desse procedimento.

### Backup do banco no volume

Copiar o arquivo `documents.db` enquanto a API está gravando pode gerar uma cópia inconsistente. Pare o contêiner antes de fazer o backup (passo 2 acima).

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
uv run pytest -v
```

Para executar os testes com relatório de cobertura do código em `app/`:

```powershell
uv run pytest --cov
```

O relatório lista as linhas não cobertas de cada arquivo. Não há percentual mínimo obrigatório.

Os testes estão localizados no diretório `tests/`.

Os testes não utilizam o arquivo `documents.db`. Cada teste recebe um banco SQLite em memória, criado do zero e descartado ao final. Nos testes da API, cada requisição usa uma sessão de banco própria, como em produção, e as verificações são feitas em uma sessão separada; assim, dados que não foram efetivamente gravados (sem `commit`) são detectados.

Os testes automatizados cobrem:

- Operações CRUD, validações de dados, tratamento de erros e normalização de textos.
- Persistência no banco de dados, operações do repositório e rollback após erros de integridade e falhas de `commit`, inclusive durante o upload de PDFs.
- Ciclo de vida da sessão (`get_db`) e configuração do banco por `DATABASE_URL`.
- Migrações: aplicação completa (`upgrade`), sincronização entre modelos e migrações (`check`), reversão (`downgrade`) e configuração do `AUTOINCREMENT`.
- Upload de PDFs válidos, com uma ou várias páginas e sem texto extraível.
- Rejeição de tipos de arquivo inválidos, assinaturas inválidas e arquivos acima de 10 MiB.
- PDFs corrompidos, protegidos por senha e erros internos do PyMuPDF.
- Limites de páginas e de tamanho do texto extraído.
- Normalização de nomes de arquivos.
- Ciclo CRUD completo de documentos criados por upload.

## Qualidade de código

O projeto utiliza o **Ruff** para lint e formatação, configurado no `pyproject.toml`:

```powershell
uv run ruff check .
uv run ruff format --check .
```

Para corrigir automaticamente a formatação, execute `uv run ruff format .`.

## Integração contínua

O workflow `.github/workflows/ci.yml` é executado no GitHub Actions a cada push e pull request para a branch `main`. Ele possui dois jobs, executados em paralelo:

1. **Code Quality and Tests:** instala as dependências com `uv sync --locked` (falha se o `uv.lock` estiver desatualizado), executa o Ruff e roda os testes com relatório de cobertura.
2. **Docker Build and Smoke Test:** constrói a imagem e executa `scripts/docker-smoke-test.sh`, que inicia o contêiner com um volume temporário e verifica o health check, a aplicação das migrações, o endpoint `/health` e a gravação no banco. O contêiner e o volume são removidos ao final, mesmo em caso de falha.

O workflow tem acesso somente de leitura ao repositório e tempo máximo de execução por job.

O smoke test também pode ser executado localmente (no Windows, pelo Git Bash). Ele usa a porta `18000` e não afeta o volume `document-intelligence-data`:

```bash
docker build -t document-intelligence-api:smoke-test .
bash scripts/docker-smoke-test.sh document-intelligence-api:smoke-test
```

## Limitações atuais

- O SQLite armazena os dados em um único arquivo e tem suporte limitado a escritas concorrentes, sendo adequado para desenvolvimento e uso local.
- O acesso ao banco de dados é síncrono.
- Os arquivos PDF não são armazenados; apenas os metadados e o texto extraído são mantidos.
- Não há OCR: PDFs digitalizados (compostos apenas por imagens) resultam em texto vazio.
- O limite de 10 MiB é verificado pela aplicação depois que o corpo da requisição já foi recebido e armazenado temporariamente pelo servidor. Para bloquear requisições muito grandes antes disso, é necessário configurar um limite em um proxy reverso ou em um middleware.
- A extração de texto é executada de forma síncrona e pode bloquear outras requisições durante o processamento de PDFs grandes.
- A listagem de documentos não possui paginação e retorna o texto extraído completo de cada PDF.
- O endpoint `/health` (e o health check do contêiner) indica apenas que a API está respondendo; ele não verifica se o banco de dados está acessível ou gravável.
- A API não possui autenticação e deve ser exposta apenas localmente.

## Próximas etapas

- Implementar a divisão do texto extraído em chunks.
- Integrar embeddings e busca vetorial.
- Desenvolver um pipeline RAG.
- Explorar agentes de IA e LangGraph.
- Evoluir a infraestrutura de testes e integração contínua.
