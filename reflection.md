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
| Normal, secret 50, guess 9 (3rd guess, even attempt) | "Too Low" / "Go HIGHER!" | Outcome is "Too High" (string comparison); score goes up 5 | none — state `score=5` after a wrong guess |
| Normal, guess "abc" then keep guessing 10 | "abc" rejected without using an attempt; 8 real guesses allowed | "abc" used an attempt; game over after 7 submissions | `[error] Out of attempts! The secret was 50. Score: -30` |
| Normal, secret 50, guess 50, then New Game, then guess 30 | New game starts; guess 30 gets a hint | Still shows "You already won"; guess ignored | `[success] You already won. Start a new game to play again.` with `status=won` |
| Easy difficulty, page load | Prompt says "between 1 and 20" | Prompt says "between 1 and 100" | `[info] Guess a number between 1 and 100. Attempts left: 5` |
| Normal, secret 50, guess 50 (first guess) | Highest score for a first-try win (100) | Final score 70 | `[success] You won! The secret was 50. Final score: 70` |

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
