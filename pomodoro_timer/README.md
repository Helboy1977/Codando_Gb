# Pomodoro Timer

Um cronômetro Pomodoro simples com interface gráfica em Tkinter.

## Funcionalidades

- Alterna entre sessões de **Foco** (25 min), **Pausa curta** (5 min) e **Pausa longa** (15 min)
- Pausa longa automática a cada 4 sessões de foco concluídas
- Contador de sessões de foco concluídas
- Aviso sonoro ao final de cada etapa
- Botões para iniciar/pausar, reiniciar e pular a etapa atual

## Como executar

Requer Python 3 com Tkinter (já incluso na instalação padrão do Python no Windows).

```bash
python pomodoro.py
```

## Requisitos

- Python 3
- Windows (o aviso sonoro usa o módulo `winsound`, específico do Windows)
