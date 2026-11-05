# 💰 API de Controle de Despesas

API REST para registrar e analisar gastos pessoais, com autenticação JWT, testes automatizados e deploy com Docker.

📖 **Documentação interativa:** `/docs`

## 🛠️ Tecnologias

- **Python 3.10+** e **FastAPI**
- **SQLAlchemy 2.0** (SQLite no desenvolvimento, PostgreSQL em produção)
- **Pydantic** para validação dos dados
- **JWT** (PyJWT) e **bcrypt** para autenticação e senhas
- **pytest** para testes automatizados
- **Docker** e **GitHub Actions** (testes rodando a cada push)

## ✨ Funcionalidades

- Cadastro e login de usuários com token JWT
- Senhas armazenadas com hash (bcrypt), nunca em texto puro
- CRUD completo de gastos
- Cada usuário enxerga **apenas os próprios gastos**
- Filtros por categoria e período, com paginação
- Resumo com total gasto e total por categoria
- Validação de dados (ex.: valor deve ser maior que zero)
- Documentação automática (Swagger) em `/docs`

## 📡 Endpoints

| Método | Rota                | Descrição                          | Auth |
|--------|---------------------|------------------------------------|------|
| POST   | `/auth/register`    | Criar conta                        | Não  |
| POST   | `/auth/login`       | Fazer login e receber o token      | Não  |
| POST   | `/expenses`         | Criar gasto                        | Sim  |
| GET    | `/expenses`         | Listar gastos (filtros: `category`, `start`, `end`, `skip`, `limit`) | Sim |
| GET    | `/expenses/summary` | Total e total por categoria        | Sim  |
| GET    | `/expenses/{id}`    | Ver um gasto                       | Sim  |
| PATCH  | `/expenses/{id}`    | Atualizar parte de um gasto        | Sim  |
| DELETE | `/expenses/{id}`    | Apagar um gasto                    | Sim  |

### Exemplo de uso

```bash
# Criar conta
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "ana", "password": "senha123"}'

# Login (devolve o access_token)
curl -X POST http://localhost:8000/auth/login \
  -d "username=ana&password=senha123"

# Criar um gasto usando o token
curl -X POST http://localhost:8000/expenses \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "Almoço", "amount": 35.5, "category": "Alimentação"}'
```

## 🚀 Como rodar localmente

```bash
# 1. Clone o repositório
git clone https://github.com/kaxinhoskx/api-controle-de-despesas.git
cd api-controle-de-despesas

# 2. Crie e ative o ambiente virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements-dev.txt

# 4. Inicie a API
uvicorn app.main:app --reload
```

Acesse **http://localhost:8000/docs** para testar todas as rotas pelo navegador. Para usar as rotas protegidas, clique em **Authorize** e faça login.

## 🧪 Testes

```bash
pytest -v
```

Os testes usam um banco SQLite em memória, então não mexem nos seus dados.

## 🐳 Docker

```bash
docker build -t api-gastos .
docker run -p 8000:8000 -e SECRET_KEY=uma-chave-bem-secreta api-gastos
```

## ⚙️ Variáveis de ambiente

| Variável          | Para que serve                                   | Padrão                     |
|-------------------|--------------------------------------------------|----------------------------|
| `SECRET_KEY`      | Chave usada para assinar os tokens JWT           | chave de desenvolvimento   |
| `DATABASE_URL`    | Endereço do banco de dados                       | `sqlite:///./gastos.db`    |
| `ALLOWED_ORIGINS` | Sites autorizados a chamar a API (separados por vírgula) | `*`                |

> ⚠️ Em produção, **sempre** defina uma `SECRET_KEY` própria e use PostgreSQL (o disco de muitos serviços gratuitos é temporário e apagaria o SQLite).

## ☁️ Deploy

O projeto tem `Dockerfile` e funciona em serviços como Render ou Railway: crie um banco PostgreSQL, conecte este repositório, defina `DATABASE_URL`, `SECRET_KEY` e `ALLOWED_ORIGINS` e faça o deploy.

## 📁 Estrutura

```
├── app/
│   ├── main.py          # criação do app, CORS e rotas
│   ├── database.py      # conexão com o banco
│   ├── models.py        # tabelas (User, Expense)
│   ├── schemas.py       # validação de entrada e saída
│   ├── security.py      # hash de senha e JWT
│   └── routers/
│       ├── auth.py      # cadastro e login
│       └── expenses.py  # CRUD, filtros e resumo
├── tests/               # testes com pytest
├── .github/workflows/   # CI (roda os testes no GitHub)
├── Dockerfile
└── requirements.txt
```

## 🧠 Decisões técnicas

- **Rotas separadas em `routers/`** para manter o código organizado conforme o projeto cresce.
- **Schemas separados dos modelos**: o que entra e sai da API não é igual ao que está no banco (por exemplo, o hash da senha nunca é devolvido).
- **404 em vez de 403** quando alguém tenta acessar o gasto de outro usuário, para não revelar que aquele gasto existe.
- **Banco em memória nos testes**, com `dependency_overrides` do FastAPI, para testes rápidos e isolados.

## 🔮 Próximos passos

- [ ] Migrações de banco com Alembic
- [ ] Usar `Decimal` em vez de `float` para valores monetários
- [ ] Refresh token
- [ ] Metas de gasto por categoria com alertas
- [ ] Integrar com o front-end do gerenciador de gastos em JS

## 📄 Licença

MIT
