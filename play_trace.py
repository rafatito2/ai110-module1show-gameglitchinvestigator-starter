"""Play scripted game sessions headlessly and print what the app shows.

Uses Streamlit's AppTest to drive app.py the same way a player would
(type a guess, click a button) and prints every message the app displays.

Run: python play_trace.py > game_trace.txt
"""
from streamlit.testing.v1 import AppTest


def show(at, action):
    """Print the action taken and every message the app displayed."""
    print(f"> {action}")
    for kind in ("info", "warning", "error", "success"):
        for el in getattr(at, kind):
            print(f"    [{kind}] {el.value}")
    print(f"    state: secret={at.session_state['secret']} "
          f"attempts={at.session_state['attempts']} "
          f"score={at.session_state['score']} "
          f"status={at.session_state['status']}")


def button(at, label):
    return next(b for b in at.button if b.label.startswith(label))


def new_session(difficulty="Normal", secret=50):
    at = AppTest.from_file("app.py").run()
    if difficulty != "Normal":
        at.sidebar.selectbox[0].select(difficulty).run()
    at.session_state["secret"] = secret
    at.run()
    print(f"\n=== New session: difficulty={difficulty}, secret forced to {secret}")
    print(f"    sidebar: {[c.value for c in at.sidebar.caption]}")
    show(at, "page loaded")
    return at


def guess(at, value):
    at.text_input[0].input(value)
    button(at, "Submit").click()
    at.run()
    show(at, f"guess {value!r}")


def main():
    # Session 1: hints on a known secret
    at = new_session("Normal", 50)
    for g in ["60", "40", "9", "100"]:
        guess(at, g)

    # Session 2: invalid input, then play until the game ends
    at = new_session("Normal", 50)
    guess(at, "abc")
    n = 1
    while at.session_state["status"] == "playing" and n < 12:
        guess(at, "10")
        n += 1
    print(f"    -> game ended after {n} submissions (limit shown: 8)")

    # Session 3: win, then press New Game
    at = new_session("Normal", 50)
    guess(at, "50")
    button(at, "New Game").click()
    at.run()
    show(at, "click New Game")
    guess(at, "30")

    # Session 4: Easy and Hard ranges
    new_session("Easy", 5)
    new_session("Hard", 25)


if __name__ == "__main__":
    main()
