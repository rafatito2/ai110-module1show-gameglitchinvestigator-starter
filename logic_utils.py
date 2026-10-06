"""Game logic for the number guessing game, kept separate from the UI."""
import json
import os

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

    too_low = low is not None and value < low
    too_high = high is not None and value > high
    if too_low or too_high:
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


def get_temperature(guess: int, secret: int, low: int, high: int):
    """Describe how close a guess is, relative to the size of the range.

    Returns:
        "🔥 Hot" within 5% of the range, "🌡️ Warm" within 15%,
        otherwise "🧊 Cold". A correct guess is "🎯 Exact".
    """
    distance = abs(guess - secret)
    if distance == 0:
        return "🎯 Exact"
    span = max(high - low, 1)
    if distance <= span * 0.05:
        return "🔥 Hot"
    if distance <= span * 0.15:
        return "🌡️ Warm"
    return "🧊 Cold"


def load_high_scores(path: str):
    """Load the best score per difficulty from a JSON file.

    A missing or unreadable file means no high scores yet.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def record_high_score(path: str, difficulty: str, score: int):
    """Save score as the best for this difficulty if it beats the old best.

    Returns:
        True if score is a new high score, otherwise False.
    """
    scores = load_high_scores(path)
    best = scores.get(difficulty)
    if best is not None and score <= best:
        return False
    scores[difficulty] = score
    with open(path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)
    return True
