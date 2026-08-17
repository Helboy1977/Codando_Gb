import tkinter as tk
import winsound

from pomodoro_logic import MODES, PomodoroState

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

        self.state = PomodoroState()
        self.after_id = None

        self.root.configure(bg="#1e1e1e")

        self.mode_label = tk.Label(
            root, text=self.state.mode, font=("Segoe UI", 18, "bold"),
            fg=MODE_COLORS[self.state.mode], bg="#1e1e1e",
        )
        self.mode_label.pack(pady=(30, 10))

        self.time_label = tk.Label(
            root, text=self.state.format_time(), font=("Segoe UI", 54, "bold"),
            fg="white", bg="#1e1e1e",
        )
        self.time_label.pack(pady=10)

        self.session_label = tk.Label(
            root, text=self.state.session_text(), font=("Segoe UI", 11),
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

    def toggle_running(self):
        self.state.running = not self.state.running
        self.start_button.config(text="Pausar" if self.state.running else "Iniciar")
        if self.state.running:
            self._tick()

    def _tick(self):
        if not self.state.running:
            return
        if self.state.tick():
            self._notify_end()
            self.advance_mode()
            return
        self.time_label.config(text=self.state.format_time())
        self.after_id = self.root.after(1000, self._tick)

    def _notify_end(self):
        winsound.MessageBeep(winsound.MB_ICONASTERISK)

    def set_mode(self, mode_name):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.state.set_mode(mode_name)
        self._refresh_widgets()

    def advance_mode(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.state.advance()
        self._refresh_widgets()

    def reset_timer(self):
        self.set_mode(self.state.mode)

    def _refresh_widgets(self):
        self.mode_label.config(text=self.state.mode, fg=MODE_COLORS[self.state.mode])
        self.time_label.config(text=self.state.format_time())
        self.session_label.config(text=self.state.session_text())
        self.start_button.config(text="Iniciar")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
