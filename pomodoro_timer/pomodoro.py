import tkinter as tk
from tkinter import ttk
import winsound

FOCUS_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
SESSIONS_BEFORE_LONG_BREAK = 4

MODES = {
    "Foco": FOCUS_MIN,
    "Pausa curta": SHORT_BREAK_MIN,
    "Pausa longa": LONG_BREAK_MIN,
}

MODE_COLORS = {
    "Foco": "#e15554",
    "Pausa curta": "#4d9de0",
    "Pausa longa": "#3bb273",
}


class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("360x420")
        self.root.resizable(False, False)

        self.mode = "Foco"
        self.completed_sessions = 0
        self.remaining_seconds = MODES[self.mode] * 60
        self.running = False
        self.after_id = None

        self.root.configure(bg="#1e1e1e")

        self.mode_label = tk.Label(
            root, text=self.mode, font=("Segoe UI", 18, "bold"),
            fg=MODE_COLORS[self.mode], bg="#1e1e1e",
        )
        self.mode_label.pack(pady=(30, 10))

        self.time_label = tk.Label(
            root, text=self._format_time(), font=("Segoe UI", 54, "bold"),
            fg="white", bg="#1e1e1e",
        )
        self.time_label.pack(pady=10)

        self.session_label = tk.Label(
            root, text=self._session_text(), font=("Segoe UI", 11),
            fg="#aaaaaa", bg="#1e1e1e",
        )
        self.session_label.pack(pady=(0, 20))

        button_frame = tk.Frame(root, bg="#1e1e1e")
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame, text="Iniciar", width=10, font=("Segoe UI", 11),
            command=self.toggle_running,
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.reset_button = tk.Button(
            button_frame, text="Reiniciar", width=10, font=("Segoe UI", 11),
            command=self.reset_timer,
        )
        self.reset_button.grid(row=0, column=1, padx=5)

        self.skip_button = tk.Button(
            root, text="Pular etapa", font=("Segoe UI", 10),
            command=self.advance_mode,
        )
        self.skip_button.pack(pady=15)

        mode_switch_frame = tk.Frame(root, bg="#1e1e1e")
        mode_switch_frame.pack(pady=10)
        for name in MODES:
            tk.Button(
                mode_switch_frame, text=name, font=("Segoe UI", 9),
                command=lambda n=name: self.set_mode(n),
            ).pack(side="left", padx=3)

    def _format_time(self):
        minutes, seconds = divmod(self.remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _session_text(self):
        return f"Sessões de foco concluídas: {self.completed_sessions}"

    def toggle_running(self):
        self.running = not self.running
        self.start_button.config(text="Pausar" if self.running else "Iniciar")
        if self.running:
            self._tick()

    def _tick(self):
        if not self.running:
            return
        if self.remaining_seconds <= 0:
            self._notify_end()
            self.advance_mode()
            return
        self.time_label.config(text=self._format_time())
        self.remaining_seconds -= 1
        self.after_id = self.root.after(1000, self._tick)

    def _notify_end(self):
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

    def set_mode(self, mode_name):
        self.running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.mode = mode_name
        self.remaining_seconds = MODES[mode_name] * 60
        self.mode_label.config(text=mode_name, fg=MODE_COLORS[mode_name])
        self.time_label.config(text=self._format_time())
        self.start_button.config(text="Iniciar")

    def advance_mode(self):
        if self.mode == "Foco":
            self.completed_sessions += 1
            self.session_label.config(text=self._session_text())
            next_mode = (
                "Pausa longa"
                if self.completed_sessions % SESSIONS_BEFORE_LONG_BREAK == 0
                else "Pausa curta"
            )
        else:
            next_mode = "Foco"
        self.set_mode(next_mode)

    def reset_timer(self):
        self.set_mode(self.mode)


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
