import os
import random
import streamlit as st

from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    get_temperature,
    load_high_scores,
    parse_guess,
    record_high_score,
    update_score,
)

HIGH_SCORE_FILE = os.environ.get(
    "HIGH_SCORE_FILE",
    os.path.join(os.path.dirname(__file__), "highscores.json"),
)

# Hint box color by closeness: red when hot, blue when cold.
HINT_STYLE = {
    "🔥 Hot": st.error,
    "🌡️ Warm": st.warning,
    "🧊 Cold": st.info,
}

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}


def start_new_game(difficulty: str):
    """Reset every piece of game state for a fresh game at this difficulty."""
    # FIX: New Game only reset attempts and the secret, so status stayed
    # "won"/"lost" and the game could not be played again.
    low, high = get_range_for_difficulty(difficulty)
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0  # FIX: started at 1, costing one guess
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty
    st.session_state.new_high_score = False


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = ATTEMPT_LIMITS[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

st.sidebar.header("🏆 High Scores")
high_scores = load_high_scores(HIGH_SCORE_FILE)
for level in ATTEMPT_LIMITS:
    best = high_scores.get(level)
    st.sidebar.caption(f"{level}: {best if best is not None else '—'}")

# FIX: changing difficulty kept the old secret, which could be out of range.
if st.session_state.get("difficulty") != difficulty:
    start_new_game(difficulty)

st.subheader("Make a guess")

# Filled in after the guess is processed so the count is never one behind.
status_box = st.empty()

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game(difficulty)
    st.success("New game started.")
    st.rerun()

if submit and st.session_state.status == "playing":
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: invalid input no longer uses up an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1

        # FIX: the secret was passed as a string on even attempts.
        outcome, message = check_guess(guess_int, st.session_state.secret)
        closeness = get_temperature(
            guess_int, st.session_state.secret, low, high
        )
        st.session_state.history.append({
            "Attempt": st.session_state.attempts,
            "Guess": guess_int,
            "Hint": outcome,
            "Closeness": closeness,
        })

        if show_hint and outcome != "Win":
            HINT_STYLE[closeness](f"{message} {closeness}")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.session_state.new_high_score = record_high_score(
                HIGH_SCORE_FILE, difficulty, st.session_state.score
            )
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"

if st.session_state.status == "won":
    st.success(
        f"You won! The secret was {st.session_state.secret}. "
        f"Final score: {st.session_state.score}. "
        "Start a new game to play again."
    )
    if st.session_state.new_high_score:
        st.success(f"🏆 New {difficulty} high score!")
elif st.session_state.status == "lost":
    st.error(
        f"Out of attempts! The secret was {st.session_state.secret}. "
        f"Score: {st.session_state.score}. Start a new game to try again."
    )

# FIX: the prompt always said 1 to 100, whatever the difficulty.
status_box.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

if st.session_state.history:
    st.subheader("📋 This game")
    st.table(st.session_state.history)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
