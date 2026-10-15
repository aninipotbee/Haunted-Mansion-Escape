# Haunted Mansion Escape (Group 7)

A small turn-based Tkinter game for the Python Game Development midterm lab exam.

## Objective
Find the **Brass Key** and the **Silver Key**, then reach the **Front Gate** before the ghost catches you.

## Rules
- Every action (move, search, analyze, solve, hint) costs one turn.
- The ghost moves one room toward you every 5 turns. If it enters your room, you lose.
- Search rooms to collect clues into your journal.
- Analyze clues to learn the answers to the puzzles in the Study and the Attic.
- Solving a puzzle gives you a key. The gate opens only when you hold both keys.
- Win: reach the Front Gate with both keys. Lose: the ghost catches you. You can restart or quit afterward.

## Controls
| Key / Button | Action |
|---|---|
| 1, 2, 3 (or exit buttons) | Move to a connected room |
| S | Search the room |
| A | Analyze the most relevant unanalyzed clue |
| P | Solve the puzzle in the current room |
| R | Rank clues by relevance |
| H | Hint: shows the route to the next objective |
| N | New game |

## Team members and roles
| Member | Primary role | Coding contribution |
|---|---|---|
| Jenica Vallente| Team coordinator and integrator | (e.g. GameState, _end_turn, integration) |
| Anilynn Pangca| Gameplay programmer | (e.g. move, search_room, win/loss rules) |
| Kent Sungahid| Data structures and algorithms programmer | (e.g. bubble_sort, insertion_insert, selection_pick) |
| Psalm Esther Nissi Waslo | Interface and asset designer | (e.g. main.py map drawing and buttons) |
| Daisy Jane Mantalaba | QA, documentation, release | (e.g. test_game_logic.py, README, find_path tests) |

## Technical info
- Framework: Tkinter (included with Python)
- Python version: 3.10
- Setup: `git clone <repo-url>` then `cd` into the folder. No packages to install.
  On Linux, if Tkinter is missing: `sudo apt install python3-tk`
- Launch: `python main.py`
- Tests: `python -m unittest -v`

## Feature map (where each required concept appears)
| Concept | File and function | How it affects play |
|---|---|---|
| Bubble Sort | `game_logic.py` `bubble_sort()`, called by `GameState.ranked_clues()` | The Rank button lists clues from most to least relevant |
| Insertion Sort | `game_logic.py` `insertion_insert()`, called by `GameState.search_room()` | Each new clue is inserted into the alphabetical journal |
| Selection Sort | `game_logic.py` `selection_pick()`, called by `GameState.analyze_best_clue()` | Selects the most relevant unanalyzed clue, which reveals puzzle answers |
| Tuple | `ROOMS[room]["pos"]` in `game_logic.py`, unpacked in `main.py` `cell_origin()` | Room (column, row) positions draw the map |
| Set | `GameState.keys`, `.searched`, `.visited`, `REQUIRED_KEYS` | Unique keys and rooms; the gate checks `REQUIRED_KEYS <= keys` |
| Dictionary | `ROOMS`, `CLUES`, `PUZZLES`, clue and puzzle records | Stores room links, clue data, and puzzle state |
| Recursion | `game_logic.py` `find_path()`, called by `ghost_step()` and `GameState.hint()` | Ghost chases you and the hint shows a route; base case is `current == target` or no unvisited neighbours |

## Credits
No external assets. All graphics are drawn with the Tkinter canvas.
