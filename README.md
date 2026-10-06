# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the game: `python -m streamlit run app.py`
3. Run the tests: `python -m pytest -v`
4. Replay the scripted game sessions: `python play_trace.py`

## 📝 Document Your Experience

**Purpose.** A Streamlit number guessing game. The player picks a difficulty, guesses a secret number within that difficulty's range and gets a higher/lower hint after each guess. Fewer attempts means a higher score. An AI wrote the starter version, and it was full of bugs.

**Bugs found.** All six are reproduced in [`game_trace_before.txt`](game_trace_before.txt) and explained in [`reflection.md`](reflection.md):

1. Hints were backwards ("Go HIGHER!" when the guess was too high).
2. On every even attempt the secret was turned into a string, so numbers were compared as text and `9` against `50` came out "Too High".
3. Attempts started at 1, so Normal allowed 7 guesses instead of 8. Invalid input like "abc" also used up an attempt.
4. New Game never reset the win/loss status, so after one game you could not play again.
5. Hard used 1–50, a smaller range than Normal. The prompt always said "between 1 and 100", whatever the difficulty.
6. Scoring: a first-try win gave 70 points, and some wrong guesses added points.

**Fixes applied.** All game logic now lives in `logic_utils.py` and `app.py` only handles the UI.

| Bug | Fix | Where |
|-----|-----|-------|
| 1 | Swapped the two hint messages | `check_guess` |
| 2 | Always pass the secret as an int; removed the `TypeError` fallback that compared strings | `app.py` submit handler, `check_guess` |
| 3 | Attempts start at 0 and only count after the input parses | `start_new_game`, submit handler |
| 4 | New Game resets secret, attempts, score, status and history, using the current difficulty's range. Changing difficulty also starts a new game | `start_new_game` |
| 5 | Hard is now 1–200; the prompt shows the real range | `get_range_for_difficulty`, `status_box` |
| 6 | Win = 100 − 10 per extra attempt (minimum 10); every wrong guess −5 | `update_score` |

Also fixed: `parse_guess` used to truncate decimals ("3.9" became 3) and accepted numbers outside the range. It now rejects both with a message. The "Attempts left" count used to lag one guess behind, because it was drawn before the guess was processed.

## 📸 Demo Walkthrough

This sample game is taken from [`game_trace_after.txt`](game_trace_after.txt) (Normal difficulty, secret 50):

1. The page loads with "Guess a number between 1 and 100. Attempts left: 8".
2. The player enters `abc`. The game shows "Enter a whole number, like 42." and attempts left stays at 8.
3. The player guesses `60`. The game shows "📉 Go LOWER! 🌡️ Warm" in a yellow box. Attempts left is 7, score −5.
4. The player guesses `40`. The game shows "📈 Go HIGHER! 🌡️ Warm". Attempts left is 6, score −10.
5. The player guesses `9`. The game shows "📈 Go HIGHER! 🧊 Cold" in a blue box. In the starter code, this guess was wrongly called "Too High".
6. The player guesses `50`. Balloons appear, then "You won! The secret was 50. Final score: 55" (a 4th-attempt win is worth 70, minus 3 × 5 for the wrong guesses) and "🏆 New Normal high score!". The sidebar shows "Normal: 55" from now on.
7. The player clicks New Game. A new secret is drawn, attempts left resets to 8 and the next guess gets a hint. In the starter code, the game stayed stuck on "You already won".

## 🧪 Test Results

20 tests: 10 in `tests/test_game_logic.py` for the bug fixes, and 10 in `tests/test_edge_cases.py` for edge cases, the hot/cold hint and the high-score file. The full output is also in [`test_results.txt`](test_results.txt).

```
$ python -m pytest -v
collecting ... collected 20 items

tests/test_edge_cases.py::test_non_numeric_text_is_rejected PASSED       [  5%]
tests/test_edge_cases.py::test_decimal_is_rejected_not_truncated PASSED  [ 10%]
tests/test_edge_cases.py::test_negative_number_is_out_of_range PASSED    [ 15%]
tests/test_edge_cases.py::test_huge_number_is_out_of_range PASSED        [ 20%]
tests/test_edge_cases.py::test_empty_and_blank_input_ask_for_a_guess PASSED [ 25%]
tests/test_edge_cases.py::test_surrounding_spaces_are_ignored PASSED     [ 30%]
tests/test_edge_cases.py::test_range_boundaries_are_inclusive PASSED     [ 35%]
tests/test_edge_cases.py::test_temperature_scales_with_range PASSED      [ 40%]
tests/test_edge_cases.py::test_high_score_only_saved_when_beaten PASSED  [ 45%]
tests/test_edge_cases.py::test_corrupt_high_score_file_is_treated_as_empty PASSED [ 50%]
tests/test_game_logic.py::test_winning_guess PASSED                      [ 55%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [ 60%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 65%]
tests/test_game_logic.py::test_too_high_hint_says_go_lower PASSED        [ 70%]
tests/test_game_logic.py::test_too_low_hint_says_go_higher PASSED        [ 75%]
tests/test_game_logic.py::test_single_digit_guess_against_two_digit_secret PASSED [ 80%]
tests/test_game_logic.py::test_harder_difficulty_has_wider_range PASSED  [ 85%]
tests/test_game_logic.py::test_first_try_win_scores_100 PASSED           [ 90%]
tests/test_game_logic.py::test_wrong_guesses_never_add_points PASSED     [ 95%]
tests/test_game_logic.py::test_valid_guess_parses PASSED                 [100%]

============================== 20 passed in 0.03s ==============================
```

## 🚀 Stretch Features

- **Advanced edge-case testing:** `tests/test_edge_cases.py` covers non-numeric text, decimals, negative and huge numbers, empty or blank input, surrounding spaces and range boundaries. The prompts and the reason for each case are in [`ai_interactions.md`](ai_interactions.md).
- **Feature expansion (High Score tracker):** the best score for each difficulty is saved to `highscores.json` and listed in the sidebar under "🏆 High Scores". A win that beats the old best shows "🏆 New … high score!". Code: `load_high_scores` and `record_high_score` in `logic_utils.py`, plus the sidebar section and win branch in `app.py`. The agent workflow is documented in `ai_interactions.md`.
- **Professional documentation and style:** every function in `logic_utils.py` has a docstring, and the code passes `flake8` with no warnings. See [`lint_report.txt`](lint_report.txt).
- **Enhanced UI:**
  - *Hot/cold closeness:* `get_temperature` in `logic_utils.py` returns 🔥 Hot (within 5% of the range), 🌡️ Warm (within 15%) or 🧊 Cold, and it is added to every hint.
  - *Color-coded hints:* the `HINT_STYLE` map in `app.py` shows hot hints in a red box, warm in yellow and cold in blue.
  - *Session table:* a "📋 This game" table (`st.table(st.session_state.history)`) lists each attempt's guess, outcome and closeness.
- **AI model comparison:** two Claude models were given the same bug (the string-secret bug). The comparison is in `ai_interactions.md`.
