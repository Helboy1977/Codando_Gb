# Gabriel Sandre — Portfólio

![Tests](https://img.shields.io/github/actions/workflow/status/Gabriel-Sandre/Codando_Gb/tests.yml?branch=main&style=flat-square&label=tests)
![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-embedded-07405E?style=flat-square&logo=sqlite&logoColor=white)
![License](https://img.shields.io/github/license/Gabriel-Sandre/Codando_Gb?style=flat-square)
![Last commit](https://img.shields.io/github/last-commit/Gabriel-Sandre/Codando_Gb?style=flat-square)

Repositório com projetos desenvolvidos para praticar e demonstrar habilidades em desenvolvimento web e programação, com foco em vagas de estágio em tecnologia. Cada projeto é funcional, testado e documentado individualmente.

## 🧩 Projetos

### 💰 [Controle de Gastos](./expense-tracker)

Aplicação full-stack para registrar e visualizar gastos por categoria, com API REST em Flask, persistência em SQLite e gráfico de distribuição no front-end.

- Cadastro, listagem e remoção de gastos, com validação no front e no back-end
- Resumo com total gasto e gráfico (doughnut) de distribuição por categoria via Chart.js

`Python` `Flask` `SQLAlchemy` `JavaScript` `Chart.js` `pytest`

→ [Ver código](./expense-tracker) · [Como rodar](./expense-tracker/README.md#como-rodar-localmente)

### 🛡️ [Monitor de Segurança de Logs](./log-security-monitor)

Aplicação que analisa logs de autenticação SSH e gera alertas automáticos de segurança, com dashboard web para visualização — projeto de cibersegurança aplicada.

- Detecção de força bruta, usuários inválidos e possíveis contas comprometidas por análise de padrões e janela de tempo
- Dashboard com resumo por severidade, ranking de IPs mais ativos e tabela de alertas filtrável

`Python` `Flask` `SQLAlchemy` `JavaScript` `Chart.js` `pytest`

→ [Ver código](./log-security-monitor) · [Como rodar](./log-security-monitor/README.md#como-rodar-localmente)

### ⏱️ [Pomodoro Timer](./pomodoro_timer)

Cronômetro Pomodoro com interface gráfica em Tkinter, alternando entre sessões de foco e pausas.

- Pausa longa automática a cada 4 sessões de foco concluídas, com contador de sessões
- Lógica de estado separada da interface (`pomodoro_logic.py`), testada com pytest

`Python` `Tkinter` `pytest`

→ [Ver código](./pomodoro_timer) · [Como rodar](./pomodoro_timer/README.md#como-rodar-localmente)

## 🛠️ Stack

`Python` · `Flask` / `Flask-SQLAlchemy` · `SQLite` · `HTML/CSS/JavaScript` · `Chart.js` · `pytest`

## Sobre

Em desenvolvimento — este repositório é atualizado conforme novos projetos são concluídos. Cada projeto tem seu próprio README com detalhes de funcionalidades, stack e instruções para rodar localmente.

## 📫 Contato

[![GitHub](https://img.shields.io/badge/GitHub-@Gabriel--Sandre-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/Gabriel-Sandre)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Gabriel_Sandre-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/sandregabriel/)
