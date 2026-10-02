import unittest

from algorithms.fifo import FIFO


class TestFIFO(unittest.TestCase):

    def setUp(self):
        self.fifo = FIFO()

    def test_add_pages(self):
        self.fifo.add_page(1)
        self.fifo.add_page(2)
        self.fifo.add_page(3)

        self.assertEqual(
            self.fifo.get_queue(),
            [1, 2, 3]
        )

    def test_select_victim(self):
        self.fifo.add_page(1)
        self.fifo.add_page(2)
        self.fifo.add_page(3)

        self.assertEqual(self.fifo.select_victim(), 1)
        self.assertEqual(self.fifo.get_queue(), [2, 3])

    def test_remove_page(self):
        self.fifo.add_page(1)
        self.fifo.add_page(2)
        self.fifo.remove_page(1)

        self.assertEqual(self.fifo.get_queue(), [2])

    def test_empty_queue(self):
        with self.assertRaises(MemoryError):
            self.fifo.select_victim()


if __name__ == "__main__":
    unittest.main()
