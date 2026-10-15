"""
game_logic.py - Haunted Mansion Escape: game rules and data (NO GUI code here).

WHERE EACH REQUIRED CONCEPT LIVES
  Bubble Sort    -> bubble_sort()       used by GameState.ranked_clues()
  Insertion Sort -> insertion_insert()  used by GameState.search_room() (ordered journal)
  Selection Sort -> selection_pick()    used by GameState.analyze_best_clue()
  Tuple          -> ROOMS[room]["pos"]  (column, row) used by main.py to draw the map
  Set            -> GameState.keys, GameState.searched, GameState.visited, REQUIRED_KEYS
  Dictionary     -> ROOMS, CLUES, PUZZLES, and each clue/puzzle record
  Recursion      -> find_path()         used by the ghost AI and the Hint button
"""

import copy

ROOMS = {
    "Front Gate": {"pos": (0, 0), "exits": ["Foyer"]},
    "Foyer":      {"pos": (0, 1), "exits": ["Front Gate", "Library", "Kitchen"]},
    "Library":    {"pos": (1, 1), "exits": ["Foyer", "Study"]},
    "Study":      {"pos": (2, 1), "exits": ["Library", "Attic"]},
    "Attic":      {"pos": (2, 0), "exits": ["Study"]},
    "Kitchen":    {"pos": (0, 2), "exits": ["Foyer", "Cellar"]},
    "Cellar":     {"pos": (0, 3), "exits": ["Kitchen", "Ballroom"]},
    "Ballroom":   {"pos": (1, 3), "exits": ["Cellar"]},
}

CLUES = {
    "Library":  {"name": "Diary Page",       "relevance": 7,
                 "hint": "The diary's last entry is dated 1893, the year of the fire."},
    "Study":    {"name": "Bloody Letter",    "relevance": 9,
                 "hint": "The letter is signed 'Isaiah'."},
    "Kitchen":  {"name": "Muddy Footprints", "relevance": 3,
                 "hint": "The footprints lead toward the cellar. Nothing more."},
    "Cellar":   {"name": "Old Photograph",   "relevance": 6,
                 "hint": "A family portrait. The youngest son is circled."},
    "Attic":    {"name": "Ghost's Locket",   "relevance": 10,
                 "hint": "The locket is empty. The ghost seems sad, not angry."},
    "Ballroom": {"name": "Broken Music Box", "relevance": 5,
                 "hint": "It plays a lullaby that echoes through the house."},
}

PUZZLES = {
    "Study": {"question": "The study safe needs a 4-digit year.\n"
                          "What year does the diary's last entry end?",
              "answer": "1893", "reward": "Brass Key", "solved": False},
    "Attic": {"question": "A chest asks: whose name signed the bloody letter?",
              "answer": "isaiah", "reward": "Silver Key", "solved": False},
}

REQUIRED_KEYS = {"Brass Key", "Silver Key"}  
START_ROOM = "Foyer"
GHOST_START = "Ballroom"


def bubble_sort(items, key="relevance", descending=True):
    """BUBBLE SORT: repeatedly compare adjacent items and swap if out of order."""
    data = list(items)                       #
    n = len(data)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            left, right = data[j][key], data[j + 1][key]
            out_of_order = left < right if descending else left > right
            if out_of_order:
                data[j], data[j + 1] = data[j + 1], data[j]
                swapped = True
        if not swapped:                     
            break
    return data


def insertion_insert(ordered, new_item, key="name"):
    """INSERTION SORT step: insert new_item into an already ordered list
    (ascending by key). Mutates and returns the list."""
    ordered.append(new_item)
    i = len(ordered) - 1
    while i > 0 and ordered[i - 1][key] > ordered[i][key]:
        ordered[i - 1], ordered[i] = ordered[i], ordered[i - 1]
        i -= 1
    return ordered


def insertion_sort(items, key="name"):
    """Full insertion sort built from repeated insertion_insert() calls."""
    result = []
    for item in items:
        insertion_insert(result, item, key)
    return result


def selection_pick(items, key="relevance", largest=True):
    """SELECTION SORT step: scan the remaining items and select the best one.
    Returns None for an empty list."""
    if not items:
        return None
    best = 0
    for i in range(1, len(items)):
        if largest:
            better = items[i][key] > items[best][key]
        else:
            better = items[i][key] < items[best][key]
        if better:
            best = i
    return items[best]


def selection_sort(items, key="relevance", descending=True):
    """Full SELECTION SORT: put the best remaining item at position i."""
    data = list(items)
    for i in range(len(data)):
        best = i
        for j in range(i + 1, len(data)):
            if descending:
                better = data[j][key] > data[best][key]
            else:
                better = data[j][key] < data[best][key]
            if better:
                best = j
        data[i], data[best] = data[best], data[i]
    return data


def find_path(rooms, current, target, visited=()):
    """Recursively search connected rooms and return the SHORTEST list of room
    names from current to target (or None if unreachable).

    Base case 1: current == target  -> path is just [current].
    Base case 2: every neighbour is already visited -> no path (None).
    Each recursive call adds a room to 'visited', so the search always makes
    progress toward a base case (the mansion has a finite number of rooms)."""
    if current == target:
        return [current]
    best = None
    for nxt in rooms[current]["exits"]:
        if nxt in visited or nxt == current:
            continue
        sub_path = find_path(rooms, nxt, target, visited + (current,))
        if sub_path is not None and (best is None or len(sub_path) + 1 < len(best)):
            best = [current] + sub_path
    return best


def ghost_step(ghost_room, player_room):
    """Ghost moves one room along the recursive path toward the player."""
    path = find_path(ROOMS, ghost_room, player_room)
    if path is not None and len(path) > 1:
        return path[1]
    return ghost_room


class GameState:
    GHOST_EVERY = 5        

    def __init__(self):
        self.player = START_ROOM
        self.ghost = GHOST_START
        self.turns = 0
        self.status = "playing"              
        self.keys = set()                    
        self.searched = set()                
        self.visited = {START_ROOM}          
        self.journal = []                   
        self.puzzles = copy.deepcopy(PUZZLES)

    def exits(self):
        return ROOMS[self.player]["exits"]

    def ghost_distance(self):
        path = find_path(ROOMS, self.ghost, self.player)
        return len(path) - 1 if path else 0

    def puzzle_here(self):
        puzzle = self.puzzles.get(self.player)
        if puzzle is not None and not puzzle["solved"]:
            return puzzle
        return None

    def _end_turn(self):
        """Every action that uses a turn ends here. The ghost may move."""
        self.turns += 1
        note = ""
        if self.turns % self.GHOST_EVERY == 0:
            self.ghost = ghost_step(self.ghost, self.player)
            note = " You hear the ghost drifting closer..."
        if self.ghost == self.player:
            self.status = "lost"
            note += " The ghost caught you!"
        return note

    def move(self, dest):
        if self.status != "playing":
            return "The game is over."
        if dest not in self.exits():
            return "You can't go there from here."
        if dest == "Front Gate" and not REQUIRED_KEYS <= self.keys:
            missing = sorted(REQUIRED_KEYS - self.keys)
            return "The gate is locked! You still need: " + ", ".join(missing) + "."
        self.player = dest
        self.visited.add(dest)
        if dest == "Front Gate":
            self.status = "won"
            return "You unlock the gate and escape the mansion!"
        return f"You walk into the {dest}." + self._end_turn()

    def search_room(self):
        if self.status != "playing":
            return "The game is over."
        if self.player in self.searched:
            return "You already searched this room."
        if self.player not in CLUES:
            return "There is nothing to find here."
        self.searched.add(self.player)
        clue = dict(CLUES[self.player])
        clue["room"] = self.player
        clue["analyzed"] = False
        insertion_insert(self.journal, clue, "name")     
        return f"You found a clue: {clue['name']}!" + self._end_turn()

    def analyze_best_clue(self):
        """Uses SELECTION SORT logic to pick the most relevant unanalyzed clue."""
        if self.status != "playing":
            return "The game is over."
        unanalyzed = [c for c in self.journal if not c["analyzed"]]
        if not self.journal:
            return "Your journal is empty. Search rooms for clues first."
        best = selection_pick(unanalyzed, "relevance", largest=True)
        if best is None:
            return "You have already analyzed every clue you found."
        best["analyzed"] = True
        return (f"You analyze the {best['name']} (relevance {best['relevance']}): "
                f"{best['hint']}" + self._end_turn())

    def solve_puzzle(self, answer):
        if self.status != "playing":
            return "The game is over."
        puzzle = self.puzzle_here()
        if puzzle is None:
            return "There is no unsolved puzzle in this room."
        if answer.strip().lower() == puzzle["answer"]:
            puzzle["solved"] = True
            self.keys.add(puzzle["reward"])
            return f"Correct! You obtained the {puzzle['reward']}!" + self._end_turn()
        return "Wrong answer. The lock stays shut." + self._end_turn()

    def ranked_clues(self):
        """BUBBLE SORT: rank the clues in the journal from most to least relevant."""
        return bubble_sort(self.journal, "relevance", descending=True)

    def hint_target(self):
        if "Brass Key" not in self.keys:
            return "Study"
        if "Silver Key" not in self.keys:
            return "Attic"
        return "Front Gate"

    def hint(self):
        """RECURSION: show the shortest route to the next objective."""
        if self.status != "playing":
            return "The game is over."
        target = self.hint_target()
        path = find_path(ROOMS, self.player, target)
        if path is None or len(path) == 1:
            return f"You are already at your objective ({target}). Search or solve the puzzle here."
        return "Next objective: " + target + ". Route: " + " -> ".join(path) + "." + self._end_turn()
