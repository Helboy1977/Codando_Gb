"""Estado e regras de transição do Pomodoro, sem dependência de interface gráfica."""

FOCUS_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
SESSIONS_BEFORE_LONG_BREAK = 4

MODES = {
    "Foco": FOCUS_MIN,
    "Pausa curta": SHORT_BREAK_MIN,
    "Pausa longa": LONG_BREAK_MIN,
}


class PomodoroState:
    def __init__(self):
        self.mode = "Foco"
        self.completed_sessions = 0
        self.remaining_seconds = MODES[self.mode] * 60
        self.running = False

    def format_time(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def session_text(self):
        return f"Sessões de foco concluídas: {self.completed_sessions}"

    def set_mode(self, mode_name):
        self.running = False
        self.mode = mode_name
        self.remaining_seconds = MODES[mode_name] * 60

    def tick(self):
        """Avança 1 segundo. Retorna True quando a etapa chega a zero."""
        if self.remaining_seconds <= 0:
            return True
        self.remaining_seconds -= 1
        return False

    def advance(self):
        """Passa para a próxima etapa (Foco -> pausa, ou pausa -> Foco)."""
        if self.mode == "Foco":
            self.completed_sessions += 1
            next_mode = (
                "Pausa longa"
                if self.completed_sessions % SESSIONS_BEFORE_LONG_BREAK == 0
                else "Pausa curta"
            )
        else:
            next_mode = "Foco"
        self.set_mode(next_mode)

    def reset(self):
        self.set_mode(self.mode)
