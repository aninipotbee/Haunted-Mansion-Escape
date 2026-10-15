"""
main.py - Haunted Mansion Escape (Tkinter interface).
Run with:  python main.py
All game rules live in game_logic.py; this file only draws screens and
forwards button clicks / key presses to the GameState.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog

from game_logic import ROOMS, CLUES, REQUIRED_KEYS, GameState

CELL_W, CELL_H, GAP = 120, 70, 35
BG = "#14141f"
FG = "#e8e8f0"

INTRO = (
    "Welcome to HAUNTED MANSION ESCAPE!\n"
    "GOAL: find the Brass Key and the Silver Key, then reach the Front Gate\n"
    "before the ghost (white G) catches you.\n"
    "HOW: search rooms for clues, analyze clues to learn puzzle answers,\n"
    "solve puzzles to get keys. Every action costs a turn and the ghost\n"
    "moves one room toward you every 5 turns.\n"
    "Controls: number keys = move, S = search, A = analyze best clue,\n"
    "P = solve puzzle, R = rank clues, H = hint, N = new game."
)


class HauntedApp:
    def __init__(self, root):
        self.root = root
        root.title("Haunted Mansion Escape")
        root.configure(bg=BG)
        root.resizable(False, False)
        self.state = GameState()
        self._build_widgets()
        self._bind_keys()
        self.say(INTRO)
        self.refresh()

    # layout
    def _build_widgets(self):
        tk.Label(self.root, text="HAUNTED MANSION ESCAPE", bg=BG, fg="#ff6b6b",
                 font=("Helvetica", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=6)

        # map canvas (left)
        cols = max(r["pos"][0] for r in ROOMS.values()) + 1    
        rows = max(r["pos"][1] for r in ROOMS.values()) + 1
        self.canvas = tk.Canvas(self.root, bg="#0b0b12", highlightthickness=0,
                                width=GAP + cols * (CELL_W + GAP),
                                height=GAP + rows * (CELL_H + GAP))
        self.canvas.grid(row=1, column=0, rowspan=3, padx=8, pady=4)

        # right-hand panel
        panel = tk.Frame(self.root, bg=BG)
        panel.grid(row=1, column=1, sticky="n", padx=8)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(panel, textvariable=self.status_var, bg=BG, fg=FG,
                                     justify="left", font=("Helvetica", 10, "bold"))
        self.status_label.pack(anchor="w")

        tk.Label(panel, text="Move to:", bg=BG, fg=FG).pack(anchor="w", pady=(6, 0))
        self.exit_frame = tk.Frame(panel, bg=BG)
        self.exit_frame.pack(anchor="w")

        tk.Label(panel, text="Actions:", bg=BG, fg=FG).pack(anchor="w", pady=(6, 0))
        actions = tk.Frame(panel, bg=BG)
        actions.pack(anchor="w")
        buttons = [("Search room (S)", self.search), ("Analyze best clue (A)", self.analyze),
                   ("Solve puzzle (P)", self.solve), ("Rank clues (R)", self.rank),
                   ("Hint (H)", self.hint), ("New game (N)", self.restart),
                   ("Quit", self.root.destroy)]
        for i, (text, cmd) in enumerate(buttons):
            tk.Button(actions, text=text, command=cmd, width=20).grid(row=i // 2, column=i % 2,
                                                                      padx=2, pady=2)

        tk.Label(panel, text="Journal (alphabetical):", bg=BG, fg=FG).pack(anchor="w", pady=(6, 0))
        self.journal_box = tk.Listbox(panel, height=6, width=48)
        self.journal_box.pack(anchor="w")

        # message log (bottom)
        self.log = tk.Text(self.root, height=9, width=100, bg="#1e1e2e", fg=FG,
                           wrap="word", state="disabled")
        self.log.grid(row=4, column=0, columnspan=2, padx=8, pady=8)

    def _bind_keys(self):
        self.root.bind("<Key>", self.on_key)

    def on_key(self, event):
        ch = event.char.lower()
        actions = {"s": self.search, "a": self.analyze, "p": self.solve,
                   "r": self.rank, "h": self.hint, "n": self.restart}
        if ch in actions:
            actions[ch]()
        elif ch.isdigit() and 1 <= int(ch) <= len(self.state.exits()):
            self.move(self.state.exits()[int(ch) - 1])

    def say(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def act(self, message):
        self.say(message)
        self.refresh()
        if self.state.status == "won":
            self.finish("YOU ESCAPED!", f"You escaped in {self.state.turns} turns "
                        f"with {len(self.state.journal)}/{len(CLUES)} clues.")
        elif self.state.status == "lost":
            self.finish("GAME OVER", "The ghost caught you...")

    def finish(self, title, text):
        if messagebox.askyesno(title, text + "\n\nPlay again?"):
            self.restart()
        else:
            self.root.destroy()

    def move(self, dest):
        self.act(self.state.move(dest))

    def search(self):
        self.act(self.state.search_room())

    def analyze(self):
        self.act(self.state.analyze_best_clue())

    def hint(self):
        self.act(self.state.hint())

    def solve(self):
        puzzle = self.state.puzzle_here()
        if puzzle is None:
            self.say("There is no unsolved puzzle in this room.")
            return
        answer = simpledialog.askstring("Puzzle", puzzle["question"], parent=self.root)
        if answer is not None:                      
            self.act(self.state.solve_puzzle(answer))

    def rank(self):
        ranked = self.state.ranked_clues()       
        if not ranked:
            self.say("You have no clues to rank yet.")
            return
        lines = [f"{i + 1}. {c['name']} (relevance {c['relevance']})"
                 for i, c in enumerate(ranked)]
        self.say("Clues ranked by relevance (Bubble Sort):\n" + "\n".join(lines))

    def restart(self):
        self.state = GameState()
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.say(INTRO)
        self.refresh()

    def refresh(self):
        st = self.state
        dist = st.ghost_distance()
        keys = ", ".join(sorted(st.keys)) if st.keys else "none"
        self.status_var.set(f"Room: {st.player}   |   Turn: {st.turns}\n"
                            f"Keys: {keys}   |   Clues: {len(st.journal)}/{len(CLUES)}\n"
                            f"Ghost is {dist} room(s) away")
        self.status_label.configure(fg="#ff6b6b" if dist <= 2 else FG)

        for widget in self.exit_frame.winfo_children():
            widget.destroy()
        for i, dest in enumerate(st.exits()):
            tk.Button(self.exit_frame, text=f"{i + 1}. {dest}", width=14,
                      command=lambda d=dest: self.move(d)).pack(side="left", padx=2)

        self.journal_box.delete(0, "end")
        for clue in st.journal:
            mark = "analyzed" if clue["analyzed"] else "new"
            self.journal_box.insert("end", f"{clue['name']}  ({clue['room']}, {mark})")
        self.draw_map()

    def cell_origin(self, room):
        col, row = ROOMS[room]["pos"]               
        return GAP + col * (CELL_W + GAP), GAP + row * (CELL_H + GAP)

    def cell_center(self, room):
        x, y = self.cell_origin(room)
        return x + CELL_W // 2, y + CELL_H // 2

    def draw_map(self):
        c = self.canvas
        c.delete("all")
        for name, data in ROOMS.items():          
            for other in data["exits"]:
                x1, y1 = self.cell_center(name)
                x2, y2 = self.cell_center(other)
                c.create_line(x1, y1, x2, y2, fill="#555566", width=3)
        for name in ROOMS:                         
            x, y = self.cell_origin(name)
            if name == "Front Gate":
                fill = "#2e6e45" if REQUIRED_KEYS <= self.state.keys else "#6e2e2e"
            elif name in self.state.visited:
                fill = "#44445c"
            else:
                fill = "#26263a"
            c.create_rectangle(x, y, x + CELL_W, y + CELL_H, fill=fill, outline="#888899", width=2)
            c.create_text(x + CELL_W // 2, y + 14, text=name, fill=FG, font=("Helvetica", 10, "bold"))
        px, py = self.cell_center(self.state.player)       # player marker
        c.create_oval(px - 26, py - 8, px - 6, py + 12, fill="#4da3ff", outline="")
        c.create_text(px - 16, py + 2, text="P", fill="black", font=("Helvetica", 9, "bold"))
        gx, gy = self.cell_center(self.state.ghost)         # ghost marker
        c.create_oval(gx + 6, gy - 8, gx + 26, gy + 12, fill="#ffffff", outline="")
        c.create_text(gx + 16, gy + 2, text="G", fill="#b00020", font=("Helvetica", 9, "bold"))


if __name__ == "__main__":
    app_root = tk.Tk()
    HauntedApp(app_root)
    app_root.mainloop()
