from pomodoro_logic import MODES, PomodoroState


def test_initial_state():
    state = PomodoroState()
    assert state.mode == "Foco"
    assert state.completed_sessions == 0
    assert state.remaining_seconds == MODES["Foco"] * 60
    assert state.running is False


def test_format_time():
    state = PomodoroState()
    state.remaining_seconds = 65
    assert state.format_time() == "01:05"


def test_session_text():
    state = PomodoroState()
    state.completed_sessions = 3
    assert state.session_text() == "Sessões de foco concluídas: 3"


def test_set_mode_resets_time_and_stops_running():
    state = PomodoroState()
    state.running = True
    state.set_mode("Pausa curta")
    assert state.mode == "Pausa curta"
    assert state.remaining_seconds == MODES["Pausa curta"] * 60
    assert state.running is False


def test_tick_counts_down_and_signals_completion():
    state = PomodoroState()
    state.remaining_seconds = 2

    assert state.tick() is False
    assert state.remaining_seconds == 1

    assert state.tick() is False
    assert state.remaining_seconds == 0

    assert state.tick() is True
    assert state.remaining_seconds == 0


def test_advance_from_focus_goes_to_short_break_and_counts_session():
    state = PomodoroState()
    state.advance()
    assert state.mode == "Pausa curta"
    assert state.completed_sessions == 1


def test_advance_from_break_goes_back_to_focus():
    state = PomodoroState()
    state.set_mode("Pausa curta")
    state.advance()
    assert state.mode == "Foco"
    assert state.completed_sessions == 0


def test_long_break_after_four_focus_sessions():
    state = PomodoroState()
    for _ in range(3):
        state.advance()  # Foco -> Pausa curta
        state.advance()  # Pausa curta -> Foco
    assert state.completed_sessions == 3

    state.advance()  # 4th Foco completed -> Pausa longa
    assert state.mode == "Pausa longa"
    assert state.completed_sessions == 4


def test_reset_keeps_mode_but_restores_time():
    state = PomodoroState()
    state.set_mode("Pausa longa")
    state.remaining_seconds = 10
    state.running = True

    state.reset()

    assert state.mode == "Pausa longa"
    assert state.remaining_seconds == MODES["Pausa longa"] * 60
    assert state.running is False
