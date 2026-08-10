import unittest
from unittest.mock import patch

import qotd


class QotdSelectionTests(unittest.TestCase):
    def test_default_selection_prefers_not_yet_asked_qotds(self):
        qotds = [
            {"content": "asked", "times-asked": 1},
            {"content": "unasked", "times-asked": 0},
        ]

        with patch("qotd.random.choices", side_effect=lambda population, weights, k=1: [population[0]]):
            chosen = qotd.select_qotd(qotds, repeated="False")

        self.assertEqual(chosen["content"], "unasked")


if __name__ == "__main__":
    unittest.main()
