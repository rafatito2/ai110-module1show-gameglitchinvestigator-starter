# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The game loaded fine and looked finished, but it was not playable. With the secret at 50, guessing 60 told me to go higher and guessing 100 also told me to go higher. The page said "Attempts left: 7" before I had guessed anything, even though the sidebar said 8 attempts. After I won, New Game picked a new secret but the page stayed on "You already won", so I could not play again.

To get repeatable evidence I wrote `play_trace.py`, which uses Streamlit's `AppTest` to play scripted sessions with a fixed secret and print every message the app shows. The output for the starter code is in [`game_trace_before.txt`](game_trace_before.txt).

Bugs found, each with expected vs. actual behavior and the code that causes it (line numbers are from the starter `app.py`):

1. **Hints are backwards.** Expected: a guess above the secret says "Go LOWER". Actual: it says "Go HIGHER". Cause: `check_guess` returns the two messages swapped (lines 38 and 40).
2. **The secret turns into a string on every even attempt.** Expected: 9 vs. 50 is "Too Low". Actual: "Too High". Cause: lines 158–161 pass `str(secret)` on even attempts. Comparing an int to a str raises `TypeError`, and the fallback in `check_guess` compares the two as strings, so `"9" > "50"` because `'9' > '5'`.
3. **Off-by-one attempts, and invalid input costs an attempt.** Expected: 8 guesses on Normal, and typing "abc" should not count. Actual: the game ends after 7 submissions, and "abc" used one of them. Cause: `attempts` starts at 1 (line 96) and is incremented before the input is parsed (line 148).
4. **New Game does not start a new game.** Expected: a fresh game. Actual: "You already won" stays on screen and guesses are ignored. Cause: the New Game handler (lines 134–138) never resets `status`, `score` or `history`, sets `attempts` to 0 instead of the starting value, and draws the secret from 1–100 regardless of difficulty.
5. **Difficulty ranges are wrong.** Expected: harder levels have a wider range, and the prompt shows that range. Actual: Hard is 1–50, smaller than Normal's 1–100, and the prompt always says "between 1 and 100" (Easy is really 1–20). Cause: `get_range_for_difficulty` (line 10) and the hard-coded text on line 110.
6. **Scoring is broken.** Expected: a first-try win gives the most points, and wrong guesses never add points. Actual: a first-try win scores 70, and a "Too High" guess on an even attempt adds 5. Cause: `update_score` uses `100 - 10 * (attempt_number + 1)` and has an even/odd branch for "Too High".

**Bug Reproduction Log**

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
| Normal, secret 50, guess 60 (1st guess) | "Too High" / "Go LOWER!" | "Go HIGHER!" | none — `[warning] Go HIGHER!` in trace |
| Normal, secret 50, guess 9 (3rd guess, even attempt) | "Too Low" / "Go HIGHER!" | Outcome is "Too High" (string comparison), and score goes up 5. The message happens to read "Go HIGHER!" only because bug 1 swaps the messages back | none — state `score=5` after a wrong guess |
| Normal, guess "abc" then keep guessing 10 | "abc" rejected without using an attempt; 8 real guesses allowed | "abc" used an attempt; game over after 7 submissions | `[error] Out of attempts! The secret was 50. Score: -30` |
| Normal, secret 50, guess 50, then New Game, then guess 30 | New game starts; guess 30 gets a hint | Still shows "You already won"; guess ignored | `[success] You already won. Start a new game to play again.` with `status=won` |
| Easy difficulty, page load | Prompt says "between 1 and 20" | Prompt says "between 1 and 100" | `[info] Guess a number between 1 and 100. Attempts left: 5` |
| Normal, secret 50, guess 50 (first guess) | Highest score for a first-try win (100) | Final score 70 | `[success] You won! The secret was 50. Final score: 70` |

---

## 2. How did you use AI as a teammate?

I used Claude Code as my coding assistant. For the model comparison I also gave Claude Sonnet and Claude Haiku the same bug.

**AI explanation of a bug.** Guessing 9 against a secret of 50 said "Too High", and only on some turns, so I asked Claude to explain the comparison. It confirmed that `app.py` passes `str(secret)` on even attempts, so `9 > "50"` raises `TypeError`, and the `except` branch in `check_guess` compares `"9"` to `"50"` as text. Text comparison goes character by character, and `'9' > '5'`.

**A correct suggestion.** Claude suggested always passing the secret as an int and deleting the `try/except TypeError` fallback, not patching it. That is correct because it removes the cause: nothing should ever compare a number to a string. I verified it two ways. `test_single_digit_guess_against_two_digit_secret` passes, and the same 9-vs-50 guess in `game_trace_after.txt` now gets "Go HIGHER!" on every attempt, odd or even.

**A suggestion I did not accept as written.** Claude Haiku's fix was to also convert `secret` to `str` inside the `except` block. I rejected it because it keeps comparing text. I pasted its function into a scratch file and ran it, and `check_guess(9, "50")` still returned "Too High". It also left the backwards hints in place. Separately, Sonnet's correct fix still incremented `attempts` before parsing the input, so typing "abc" would still cost a guess. I kept its `check_guess` but moved the increment after validation. The "abc" session in `game_trace_after.txt` (one invalid input, then 8 guesses) confirms that "abc" no longer uses an attempt.

**Starter tests revised.** The starter tests compared `check_guess(...)` to a plain string such as `"Win"`, but the function returns `(outcome, message)`, so those tests could never pass. I kept the function's return shape, because the UI needs the message, and changed the tests to unpack the outcome.

---

## 3. Debugging and testing your fixes

A bug counted as fixed only when two things were true: a pytest test aimed at that exact bug passed, and the same input in the scripted game (`play_trace.py`) produced the expected message. Comparing `game_trace_before.txt` with `game_trace_after.txt` gives a before/after for every row of the bug log. For example, guess 60 against 50 changed from "Go HIGHER!" to "Go LOWER!". One test that taught me something was `test_first_try_win_scores_100`. The old formula `100 - 10 * (attempt_number + 1)` looked reasonable until the test showed a perfect game scoring 70. I used AI to speed up writing the tests, and checked that each one tests a behavior from the bug log and not how the code is written. The suite now has 20 passing tests.

---

## 4. What did you learn about Streamlit and state?

Streamlit runs the whole `app.py` script from top to bottom every time you click a button or type something, so normal variables are recreated on every click. `st.session_state` is a dictionary that survives those reruns, which is why the secret, attempts and score live there. This also explains the lagging "Attempts left" bug: the message was drawn near the top of the script, before the code further down processed the click. Fixing it meant reserving a spot with `st.empty()` and filling it in at the end of the run.

---

## 5. Looking ahead: your developer habits

- **Habit to keep:** reproduce a bug with a fixed input before fixing it, and keep that input as a test. A script with a fixed secret made every bug repeatable and showed whether a fix worked.
- **Do differently:** run an AI's fix before trusting it, even when the explanation sounds sure of itself. Haiku's answer read well but did not fix anything.
- **How my view changed:** AI-generated code can look finished and still be wrong in small ways that only show up with specific inputs. I now treat AI output as a draft that needs a test.
