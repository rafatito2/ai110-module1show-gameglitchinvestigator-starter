from logic_utils import (
    check_guess,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# check_guess returns (outcome, message), so the starter tests that compared
# the whole result to a string could never pass. They now check the outcome.

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"


# Bug 1: hints were backwards.
def test_too_high_hint_says_go_lower():
    _, message = check_guess(60, 50)
    assert "LOWER" in message


def test_too_low_hint_says_go_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message


# Bug 2: the secret became a string, so 9 vs 50 was compared as "9" > "50".
def test_single_digit_guess_against_two_digit_secret():
    outcome, _ = check_guess(9, 50)
    assert outcome == "Too Low"


# Bug 5: Hard had a smaller range than Normal.
def test_harder_difficulty_has_wider_range():
    easy = get_range_for_difficulty("Easy")
    normal = get_range_for_difficulty("Normal")
    hard = get_range_for_difficulty("Hard")
    assert easy[1] < normal[1] < hard[1]


# Bug 6: scoring.
def test_first_try_win_scores_100():
    assert update_score(0, "Win", 1) == 100


def test_wrong_guesses_never_add_points():
    for attempt in range(1, 9):
        assert update_score(0, "Too High", attempt) == -5
        assert update_score(0, "Too Low", attempt) == -5


def test_valid_guess_parses():
    assert parse_guess("42", 1, 100) == (True, 42, None)
