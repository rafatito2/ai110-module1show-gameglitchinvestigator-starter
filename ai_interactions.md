# AI Interactions Log

AI tool: **Claude Code** for the agent workflow. Claude Sonnet and Claude Haiku were used for the model comparison.

---

## Agent Workflow (SF8)

**What task did you give the agent?**

Add a High Score tracker that saves the best score per difficulty to a file and shows it in the game.

**What did the agent do?**

- `logic_utils.py`: added `load_high_scores(path)`, which treats a missing or corrupt file as "no scores yet", and `record_high_score(path, difficulty, score)`, which only writes when the old best is beaten.
- `app.py`: added a "🏆 High Scores" section in the sidebar, recorded the score in the win branch and shows "🏆 New … high score!".
- `.gitignore`: added `highscores.json`, since scores belong to each player and not to the repo.
- `tests/test_edge_cases.py`: added two tests that use pytest's `tmp_path`. One checks that a lower score never replaces a higher one, the other that a corrupt file is handled.
- Ran `pytest` and `play_trace.py` to check the feature in a real (headless) game.

**What did you have to verify or fix manually?**

After the first run, a `highscores.json` file appeared in the project folder. The scripted test games in `play_trace.py` were writing into the real high-score file. The fix was to make the file path configurable through the `HIGH_SCORE_FILE` environment variable, and have `play_trace.py` point it at a temporary folder. To check the fix, the file was deleted and the trace run again, and no new file appeared. The trace still shows "New Normal high score!" after the win.

---

## Test Generation (SF7)

Prompt to Claude Code: the "Challenge 1: Advanced Edge-Case Testing" text from the assignment, plus "find inputs that could still break the game and write pytest cases for them".

| Edge Case | Prompt Used | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Decimal `"3.9"` | Challenge 1 prompt above | `test_decimal_is_rejected_not_truncated` | Yes (the starter `parse_guess` would fail it) | The starter code silently turned 3.9 into 3. The player should be told, not have their guess changed. `parse_guess` now rejects decimals. |
| Negative `"-5"` | same | `test_negative_number_is_out_of_range` | Yes | `int("-5")` parses without error, so only a range check catches it. Before the fix it used up an attempt. |
| Huge `"99999999999999999999"` | same | `test_huge_number_is_out_of_range` | Yes | Python ints never overflow, so the risk is accepting a number outside the range, not a crash. |
| Empty, blank `"   "`, `None` | same | `test_empty_and_blank_input_ask_for_a_guess` | Yes | The starter code only checked `""`, so a guess of only spaces fell through to "That is not a number". |
| Non-numeric `"abc"` | same | `test_non_numeric_text_is_rejected` | Yes | This is the input from the bug log that used up an attempt. |
| Boundaries `1`, `100`, `0`, `101` | same | `test_range_boundaries_are_inclusive` | Yes | Off-by-one errors happen at the edges, and the range is meant to be inclusive. |

---

## Linting & Style (SF9)

**Prompt used** (the Challenge 3 task, as given to Claude Code):

```
Add professional docstrings to every function in logic_utils.py, then check
the code for PEP 8 compliance with flake8 and fix what it reports.
```

**Linting output before:**

```
$ flake8 app.py   # starter code
app.py:4:1: E302 expected 2 blank lines, found 1
app.py:67:1: E305 expected 2 blank lines after class or function definition, found 1

$ flake8 app.py logic_utils.py play_trace.py tests/   # first draft of fixes
logic_utils.py:1:80: E501 line too long (83 > 79 characters)
logic_utils.py:41:80: E501 line too long (80 > 79 characters)
play_trace.py:33:80: E501 line too long (83 > 79 characters)
```

After the changes, `flake8` reports nothing. The full output is in [`lint_report.txt`](lint_report.txt).

**Changes applied:**

- Every function in `logic_utils.py` now has a docstring that says what it returns. `parse_guess`, `check_guess`, `get_temperature` and `record_high_score` describe their tuple or boolean results explicitly.
- Added the blank lines PEP 8 expects between the functions and the top-level Streamlit code (E302/E305).
- Shortened the long module docstring, and split the long range check into two named booleans, `too_low` and `too_high`. That fixed E501 and made the condition easier to read.
- Changed `except Exception` in `parse_guess` to `except ValueError`, so real errors are not hidden.
- Not applied: no names were renamed. The existing names (`check_guess`, `parse_guess`, …) already follow PEP 8 snake_case, and renaming them would break the starter tests' imports.

---

## Model Comparison (SF11)

**Task given to both models:** the same prompt with the original `check_guess` and the even-attempt code from `app.py`. The bug report: "with the secret at 50, guessing 9 on the 3rd guess says Too High, but guessing 40 on the 2nd guess correctly says Too Low". Each model was asked for the root cause, a fix and an explanation, without tools.

| | Model A | Model B |
|-|---------|---------|
| **Model name** | Claude Sonnet | Claude Haiku |
| **Response summary** | Found the real cause. Attempts start at 1, so the 3rd guess is attempt 4 (even), the secret becomes `"50"`, the int/str comparison raises `TypeError` and the fallback compares strings (`"9" > "50"`). It also noticed the hint messages were swapped. Fix: always use the int secret, delete the `try/except`, swap the messages. | Said the problem was the `except` block comparing a string to an int. Fix: also convert `secret` to `str` inside the `except` block. |
| **Correct?** | Yes. Its `check_guess` matches the fix I kept. | No. I ran its version: `check_guess(9, "50")` still returns "Too High", because it still compares text. The backwards hints were not addressed either. |
| **More Pythonic?** | Yes. Three plain comparisons, no exception handling used for control flow. | No. It keeps the `try/except TypeError` and makes the type confusion permanent. |
| **Clearer explanation?** | Yes. It traced the exact attempt numbers and explained why the 2nd guess only looked correct. | No. The explanation describes a situation that cannot happen in this code. |

**Which did you prefer and why?**

Sonnet. It fixed the cause (the secret being turned into a string) and not just the symptom, and its explanation matched what the trace showed. I did not take its fix exactly as written, though. Its `app.py` snippet still increments `attempts` before parsing the input, so invalid input would still use up a guess (bug 3). I moved the increment after validation. Haiku's answer sounded confident but was wrong, and running it was the only way to know. It's a good example of why an AI fix should be tested before you accept it.
