from logic_utils import (
    get_temperature,
    load_high_scores,
    parse_guess,
    record_high_score,
)


# Edge cases for parse_guess (Normal range 1-100).

def test_non_numeric_text_is_rejected():
    ok, value, err = parse_guess("abc", 1, 100)
    assert not ok and value is None and "whole number" in err


def test_decimal_is_rejected_not_truncated():
    ok, value, _ = parse_guess("3.9", 1, 100)
    assert not ok and value is None


def test_negative_number_is_out_of_range():
    ok, _, err = parse_guess("-5", 1, 100)
    assert not ok and err == "Enter a number between 1 and 100."


def test_huge_number_is_out_of_range():
    ok, _, _ = parse_guess("99999999999999999999", 1, 100)
    assert not ok


def test_empty_and_blank_input_ask_for_a_guess():
    assert parse_guess("", 1, 100) == (False, None, "Enter a guess.")
    assert parse_guess("   ", 1, 100) == (False, None, "Enter a guess.")
    assert parse_guess(None, 1, 100) == (False, None, "Enter a guess.")


def test_surrounding_spaces_are_ignored():
    assert parse_guess("  42 ", 1, 100) == (True, 42, None)


def test_range_boundaries_are_inclusive():
    assert parse_guess("1", 1, 100)[0]
    assert parse_guess("100", 1, 100)[0]
    assert not parse_guess("0", 1, 100)[0]
    assert not parse_guess("101", 1, 100)[0]


# Hot/cold hint.

def test_temperature_scales_with_range():
    assert get_temperature(50, 50, 1, 100) == "🎯 Exact"
    assert get_temperature(53, 50, 1, 100) == "🔥 Hot"
    assert get_temperature(60, 50, 1, 100) == "🌡️ Warm"
    assert get_temperature(9, 50, 1, 100) == "🧊 Cold"


# High score file.

def test_high_score_only_saved_when_beaten(tmp_path):
    path = str(tmp_path / "scores.json")
    assert load_high_scores(path) == {}
    assert record_high_score(path, "Normal", 80)
    assert not record_high_score(path, "Normal", 70)
    assert record_high_score(path, "Normal", 90)
    assert load_high_scores(path) == {"Normal": 90}


def test_corrupt_high_score_file_is_treated_as_empty(tmp_path):
    path = tmp_path / "scores.json"
    path.write_text("not json")
    assert load_high_scores(str(path)) == {}
