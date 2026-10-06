"""Game logic for the number guessing game, kept separate from the Streamlit UI."""

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    "Hard": (1, 200),
}


def get_range_for_difficulty(difficulty: str):
    """Return the inclusive (low, high) range for a difficulty.

    Harder levels use a wider range. Unknown names fall back to Normal.
    """
    # FIX: Hard was 1-50, easier than Normal. Widened to 1-200.
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def parse_guess(raw: str, low: int = None, high: int = None):
    """Parse the text a player typed into a whole-number guess.

    Args:
        raw: Text from the input box. May be None or empty.
        low: Smallest allowed guess, or None for no lower limit.
        high: Largest allowed guess, or None for no upper limit.

    Returns:
        (ok, guess, error): ok is True when the input is a valid guess,
        guess is the int value (None when not ok), and error is a message
        for the player (None when ok).
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    try:
        value = int(raw.strip())
    except ValueError:
        # FIX: "3.9" used to be truncated to 3 without telling the player.
        return False, None, "Enter a whole number, like 42."

    if (low is not None and value < low) or (high is not None and value > high):
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int):
    """Compare a guess to the secret number.

    Returns:
        (outcome, message): outcome is "Win", "Too High" or "Too Low",
        and message is the hint shown to the player.
    """
    # FIX: messages were swapped, and the TypeError fallback that compared
    # numbers as text ("9" > "50") was removed. Found by replaying the trace
    # with Claude Code; the real cause was the even-attempt str() in app.py.
    if guess == secret:
        return "Win", "🎉 Correct!"
    if guess > secret:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Return the new score after a guess.

    A win on attempt 1 is worth 100 points, 10 fewer for each extra
    attempt, never less than 10. Every wrong guess costs 5 points.
    """
    # FIX: a first-try win scored 70 and some wrong guesses added points.
    if outcome == "Win":
        return current_score + max(10, 100 - 10 * (attempt_number - 1))
    if outcome in ("Too High", "Too Low"):
        return current_score - 5
    return current_score
