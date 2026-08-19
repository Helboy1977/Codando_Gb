# 🛡️ Monitor de Segurança de Logs

**▶️ Aplicação no ar: [log-security-monitor.onrender.com](https://log-security-monitor.onrender.com)**

Aplicação web que analisa logs de autenticação SSH (estilo `auth.log` do Linux) e gera alertas de segurança automaticamente, destacando possíveis ataques de força bruta, tentativas com usuários inválidos e contas possivelmente comprometidas.

> A aplicação está hospedada no plano gratuito do Render, que desliga o serviço após um período sem uso. O primeiro acesso pode levar cerca de 15 segundos até a aplicação subir; os seguintes são imediatos. Se a tabela estiver vazia, clique em **Analisar logs** para processar o arquivo de exemplo.

## Funcionalidades

- Parser de logs de autenticação SSH (`Failed password` / `Accepted password`)
- Detecção de **força bruta**: 5+ tentativas falhas do mesmo IP em menos de 2 minutos
- Detecção de **usuário inválido**: tentativas de login com usuários que não existem no sistema
- Detecção de **possível comprometimento**: login bem-sucedido logo após múltiplas falhas do mesmo IP
- Dashboard com resumo por severidade (gráfico), lista dos IPs mais ativos e tabela filtrável de alertas
- Alertas persistidos em SQLite, recriados a cada nova análise

## Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy (API REST), SQLite
- **Análise de logs:** módulo próprio (`analyzer.py`) com regex e detecção por janela de tempo, sem dependências externas
- **Frontend:** HTML, CSS e JavaScript puro, [Chart.js](https://www.chartjs.org/) para o gráfico
- **Testes:** pytest — testes unitários do analisador e testes da API

## Estrutura

```
log-security-monitor/
├── app.py                   # App Flask + modelo Alert + rotas da API
├── analyzer.py               # Parser e detecção de eventos de segurança
├── sample_logs/auth.log      # Log de exemplo (inclui um ataque de força bruta simulado)
├── templates/index.html      # Página única (dashboard)
├── static/
│   ├── css/style.css
│   └── js/app.js              # Consome a API via fetch
├── tests/
│   ├── test_analyzer.py       # Testes do parser/detecção
│   └── test_app.py            # Testes da API
└── requirements.txt
```

## Como funciona a detecção

O `analyzer.py` lê cada linha do log, identifica eventos `Failed password` e `Accepted password` e aplica regras:

| Alerta                  | Severidade | Regra                                                              |
|--------------------------|------------|---------------------------------------------------------------------|
| `failed_login`            | Baixa      | Falha de login para um usuário válido                              |
| `invalid_user`            | Média      | Falha de login para um usuário que não existe ("invalid user")     |
| `brute_force`              | Alta       | 5+ falhas do mesmo IP em até 120 segundos                          |
| `possible_compromise`      | Alta       | Login aceito de um IP que teve 3+ falhas recentes                  |

## API

| Método | Rota                          | Descrição                                    |
|--------|-------------------------------|-----------------------------------------------|
| POST   | `/api/analyze`                | Reanalisa `sample_logs/auth.log` e recria os alertas |
| GET    | `/api/alerts`                 | Lista alertas (filtros opcionais `?severity=` e `?type=`) |
| GET    | `/api/summary`                | Total, contagem por severidade e top 5 IPs    |
| DELETE | `/api/alerts`                 | Limpa todos os alertas                        |

## Como rodar localmente

```bash
cd log-security-monitor
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
python app.py
```

Acesse `http://localhost:5001` e clique em "Analisar logs".

## Rodando os testes

```bash
pytest -q
```

## Deploy

A aplicação está publicada no [Render](https://render.com), camada gratuita, em
**[log-security-monitor.onrender.com](https://log-security-monitor.onrender.com)**.
Cada alteração enviada para a branch `main` dispara um novo deploy automaticamente.

Configuração usada:

| Item | Valor |
|---|---|
| Tipo de serviço | Web Service |
| Root directory | `log-security-monitor` |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn app:app --bind 0.0.0.0:$PORT` |

O `gunicorn` substitui o servidor de desenvolvimento do Flask, que não é adequado para produção — ele atende uma requisição por vez e não foi escrito para exposição direta na internet.

### Duas limitações do plano gratuito, e o que fazer a respeito

**O disco é efêmero.** O banco SQLite é recriado a cada deploy ou reinício, então os alertas somem. Basta clicar em "Analisar logs" para repopular. Resolver isso de verdade exigiria um banco gerenciado à parte — o próprio Render oferece PostgreSQL, e a troca seria apenas na variável de conexão, já que a aplicação usa SQLAlchemy.

**O serviço hiberna.** Após um período sem tráfego o Render desliga o processo, e a requisição seguinte precisa aguardar a aplicação subir de novo — cerca de 15 segundos. Acessos posteriores são imediatos.

## Possíveis próximos passos

- Suporte a upload de um arquivo de log próprio pela interface
- Mais fontes de log (Nginx/Apache access log, Windows Event Log)
- Notificação (e-mail/webhook) quando um alerta de severidade alta é gerado
