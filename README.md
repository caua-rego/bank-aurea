<p align="center"><strong>Bank Auréa</strong> · Plataforma bancária full-stack (Flask + Angular)</p>

## Visão geral

API bancária em Flask com front-end Angular. O backend expõe autenticação, contas, transferências e perfil de usuário; o front (Angular 17/21) consome a API e entrega a UI. Arquitetura em camadas (controllers → services → models/repositories) com Flask-Login, SQLAlchemy e rate limiting básico.

## Arquitetura

- Backend: Flask, SQLAlchemy, Flask-Login, Flask-Limiter, Flask-Migrate, SQLite (padrão) ou outro via `DATABASE_URL`.
- Frontend: Angular standalone components; scripts `npm start`/`ng serve`.
- Segurança: hashing com Bcrypt; sessões e cookies SameSite=Lax; limites de requisição; CSRF desativado por operar como API JSON.

## Pré-requisitos

- Python 3.11+ (recomendado) com `pip`
- Node.js 20+ / npm 11+ (para o front)
- Postgres 14+ (default) ou outro banco compatível com SQLAlchemy
- Redis (para rate limiting em produção; em teste cai para memória)

## Como rodar rápido (backend)

1) Crie o ambiente e instale deps:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure variáveis (opcional, mas recomendado):
```bash
export FLASK_CONFIG=development
export SECRET_KEY="troque-este-valor"          # obrigatória em produção
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/aurea"
export RATELIMIT_STORAGE_URI="redis://localhost:6379/0"  # default já é Redis
```

3) Suba o schema (usa Alembic/Flask-Migrate):
```bash
flask db upgrade
```

4) Rode a API (porta 5001 por padrão):
```bash
python run.py
```

5) Testes backend:
```bash
pytest
```

## Como rodar o frontend (Angular)

```bash
cd frontend
npm install
npm start           # abre em http://localhost:4200
```

### Ajuste de CORS / origem

O backend permite origens `localhost:4200` e `localhost:5001` por padrão. Se o front rodar noutro host/porta, inclua a origem na configuração de CORS ao criar a app.

## Principais endpoints (backend)

- Autenticação
    - `POST /auth/register` — cria usuário e conta com saldo inicial.
    - `POST /auth/login` — autentica (session cookie); rate limit 10/min.
    - `POST /auth/logout` — encerra sessão.
    - `GET /auth/me` — retorna o usuário logado.
- Operações bancárias (requer login)
    - `GET /dashboard` — dados da conta, cartão e histórico.
    - `POST /transfer` — transfere para `target_account`; 10/min.
    - `POST /deposit` — depósito; 5/min.
    - `POST /withdraw` — saque; 5/min.
- Perfil
    - `PUT /users/profile` — atualiza preferências e envia imagem (JSON ou multipart).

## Dados e regras de negócio

- Cadastro cria automaticamente uma conta com saldo inicial de 1000.00.
- Transações são registradas em tabela de histórico (`transactions`) com timestamp UTC.
- Transferências usam bloqueio pessimista (`with_for_update`) em bancos que suportam; em SQLite, a semântica é best-effort.

## Variáveis de ambiente recomendadas

- `SECRET_KEY` — **defina em produção** (padrão inseguro apenas para dev).
- `DATABASE_URL` — URI SQLAlchemy; padrão é Postgres local (`postgresql+psycopg2://postgres:postgres@localhost:5432/aurea`).
- `FLASK_CONFIG` — `development` (padrão), `testing`, `production`.
- `RATELIMIT_STORAGE_URI` — default Redis local; em teste troca para memória.
- `SESSION_COOKIE_SECURE` / `REMEMBER_COOKIE_SECURE` — ajuste para `True` em HTTPS.

## Observações de segurança e operações

- CSRF está desativado (`WTF_CSRF_ENABLED=False`) porque a API é JSON; se usar cookies em produção, reavaliar.
- Rate limiting usa armazenamento em memória; para múltiplas instâncias use Redis/DB.
- Segredos (SECRET_KEY) e cookies seguros devem ser configurados antes de produção.
- A CORS list é explícita; mantenha restrita ao domínio do front.

## Estrutura

```
app/
├── controllers/    # Blueprints HTTP (auth, main, user, admin, card)
├── services/       # Regras de negócio (auth, transações)
├── models/         # User, Account, Transaction, Card
├── repositories/   # Acesso a dados (quando usado)
├── forms/          # WTForms (legado/apoio)
├── extensions.py   # Wiring de extensões Flask/SQLAlchemy
└── __init__.py     # Factory create_app

frontend/
├── src/app         # App Angular standalone + rotas
└── ...
```

## Roadmap curto

- Mover rate limiting para store compartilhado (Redis) e parametrizar via env.
- Reativar/ajustar CSRF ou migrar autenticação para tokens/bearer.
- Configurar SECRET_KEY, cookies `Secure` e HTTPS para produção.
- Adicionar lint/CI (ruff/flake8, mypy) e testes cobrindo flows de transação e upload.
- Documentar OpenAPI/Swagger e fixtures para desenvolvimento.
