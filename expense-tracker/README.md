# 💰 Controle de Gastos

Aplicação web full-stack para registrar gastos, categorizá-los e visualizar um resumo com gráfico — como um mini "onde meu dinheiro foi parar".

## Funcionalidades

- Cadastro de gastos com descrição, valor, categoria e data
- Listagem dos gastos mais recentes primeiro
- Remoção de gastos
- Resumo com total gasto e gráfico (doughnut) de distribuição por categoria
- Validação de dados tanto no front quanto na API (valor numérico positivo, categoria válida)

## Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy (API REST), SQLite
- **Frontend:** HTML, CSS e JavaScript puro (sem framework), [Chart.js](https://www.chartjs.org/) para o gráfico
- **Testes:** pytest, com fixtures usando banco de dados em memória

## Estrutura

```
expense-tracker/
├── app.py                 # App Flask + modelo + rotas da API
├── templates/index.html   # Página única
├── static/
│   ├── css/style.css
│   └── js/app.js          # Consome a API via fetch
├── tests/test_app.py      # Testes da API
└── requirements.txt
```

## API

| Método | Rota                    | Descrição                          |
|--------|-------------------------|-------------------------------------|
| GET    | `/api/expenses`         | Lista todos os gastos               |
| POST   | `/api/expenses`         | Cria um gasto                       |
| DELETE | `/api/expenses/<id>`    | Remove um gasto                     |
| GET    | `/api/summary`          | Total e soma por categoria          |

## Como rodar localmente

```bash
cd expense-tracker
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
python app.py
```

Acesse `http://localhost:5000`.

## Rodando os testes

```bash
pytest -q
```

## Possíveis próximos passos

- Autenticação de usuário (multi-usuário)
- Filtro por período/mês na interface
- Exportação dos gastos em CSV
