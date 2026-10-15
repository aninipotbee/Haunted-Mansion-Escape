"""Run with:  python -m unittest -v"""
import unittest

from game_logic import (ROOMS, GameState, bubble_sort, insertion_insert, insertion_sort,
                        selection_pick, selection_sort, find_path)

CLUES = [{"name": "C", "relevance": 5}, {"name": "A", "relevance": 9},
         {"name": "B", "relevance": 1}, {"name": "D", "relevance": 7}]


class TestSorts(unittest.TestCase):
    def test_bubble_sort(self):
        self.assertEqual(bubble_sort([]), [])
        one = [{"name": "X", "relevance": 3}]
        self.assertEqual(bubble_sort(one), one)
        result = [c["relevance"] for c in bubble_sort(CLUES, "relevance", True)]
        self.assertEqual(result, [9, 7, 5, 1])
        result = [c["relevance"] for c in bubble_sort(CLUES, "relevance", False)]
        self.assertEqual(result, [1, 5, 7, 9])

    def test_insertion_sort(self):
        self.assertEqual(insertion_sort([]), [])
        one = [{"name": "X"}]
        self.assertEqual(insertion_sort(one), one)
        self.assertEqual([c["name"] for c in insertion_sort(CLUES, "name")], ["A", "B", "C", "D"])
        ordered = [{"name": "A"}, {"name": "C"}]
        insertion_insert(ordered, {"name": "B"}, "name")
        self.assertEqual([c["name"] for c in ordered], ["A", "B", "C"])

    def test_selection_sort(self):
        self.assertEqual(selection_sort([]), [])
        self.assertIsNone(selection_pick([]))
        one = [{"name": "X", "relevance": 3}]
        self.assertEqual(selection_sort(one), one)
        self.assertEqual([c["relevance"] for c in selection_sort(CLUES)], [9, 7, 5, 1])
        self.assertEqual(selection_pick(CLUES, "relevance", True)["relevance"], 9)
        self.assertEqual(selection_pick(CLUES, "relevance", False)["relevance"], 1)


class TestRecursion(unittest.TestCase):
    def test_find_path(self):
        self.assertEqual(find_path(ROOMS, "Foyer", "Foyer"), ["Foyer"])
        self.assertEqual(find_path(ROOMS, "Foyer", "Attic"), ["Foyer", "Library", "Study", "Attic"])
        self.assertEqual(find_path(ROOMS, "Ballroom", "Foyer"),
                         ["Ballroom", "Cellar", "Kitchen", "Foyer"])


class TestGameFlow(unittest.TestCase):
    def test_win(self):
        g = GameState()
        g.move("Library"); g.search_room()
        g.move("Study"); g.search_room()
        g.analyze_best_clue(); g.analyze_best_clue()
        g.solve_puzzle("1893")
        g.move("Attic"); g.solve_puzzle("Isaiah")
        self.assertEqual(g.keys, {"Brass Key", "Silver Key"})
        g.move("Study"); g.move("Library"); g.move("Foyer"); g.move("Front Gate")
        self.assertEqual(g.status, "won")

    def test_locked_gate(self):
        g = GameState()
        self.assertIn("locked", g.move("Front Gate"))
        self.assertEqual(g.status, "playing")

    def test_lose_to_ghost(self):
        g = GameState()
        for _ in range(40):
            if g.status != "playing":
                break
            g.hint()                      
        self.assertEqual(g.status, "lost")

    def test_journal_is_alphabetical(self):
        g = GameState()
        g.move("Library"); g.search_room()
        g.move("Study"); g.search_room()
        names = [c["name"] for c in g.journal]
        self.assertEqual(names, sorted(names))


if __name__ == "__main__":
    unittest.main()
