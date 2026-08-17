# Pomodoro Timer

Um cronômetro Pomodoro simples com interface gráfica em Tkinter.

## Funcionalidades

- Alterna entre sessões de **Foco** (25 min), **Pausa curta** (5 min) e **Pausa longa** (15 min)
- Pausa longa automática a cada 4 sessões de foco concluídas
- Contador de sessões de foco concluídas
- Aviso sonoro ao final de cada etapa
- Botões para iniciar/pausar, reiniciar e pular a etapa atual

## Estrutura

A lógica de estado (contagem, transição entre etapas, formatação de tempo) fica separada da interface gráfica em `pomodoro_logic.py`, o que permite testá-la com pytest sem precisar de um display.

```
pomodoro_timer/
├── pomodoro.py                    # Interface gráfica (Tkinter)
├── pomodoro_logic.py               # Estado e regras de transição (sem dependência de GUI)
├── tests/test_pomodoro_logic.py    # Testes da lógica
└── requirements.txt
```

## Como rodar localmente

Requer Python 3 com Tkinter (já incluso na instalação padrão do Python no Windows).

```bash
cd pomodoro_timer
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
python pomodoro.py
```

## Rodando os testes

```bash
pytest -q
```

## Requisitos

- Python 3
- Windows para rodar a interface (o aviso sonoro usa o módulo `winsound`, específico do Windows) — a lógica em `pomodoro_logic.py` é multiplataforma
