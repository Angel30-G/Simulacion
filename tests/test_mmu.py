import unittest

from core.mmu import MMU


class TestMMU(unittest.TestCase):

    def setUp(self):
        self.mmu = MMU()

    def test_new(self):
        ptr = self.mmu.new(1, 500)

        self.assertEqual(ptr, 1)
        self.assertEqual(len(self.mmu.pointers[ptr].pages), 1)
        self.assertEqual(self.mmu.get_stats()["ram_used_kb"], 4)
        self.assertEqual(self.mmu.get_stats()["page_faults"], 1)
        self.assertEqual(self.mmu.get_stats()["clock"], 5)

    def test_multiple_pages(self):
        ptr = self.mmu.new(1, 5000)

        self.assertEqual(len(self.mmu.pointers[ptr].pages), 2)
        self.assertEqual(self.mmu.get_stats()["ram_used_kb"], 8)
        self.assertEqual(self.mmu.get_stats()["page_faults"], 2)

    def test_use(self):
        ptr = self.mmu.new(1, 500)

        self.mmu.use(ptr)

        stats = self.mmu.get_stats()
        self.assertEqual(stats["page_hits"], 1)
        self.assertEqual(stats["clock"], 6)

    def test_delete(self):
        ptr = self.mmu.new(1, 500)

        self.mmu.delete(ptr)

        self.assertEqual(self.mmu.get_stats()["ram_used_kb"], 0)
        self.assertEqual(self.mmu.get_stats()["fragmentation_bytes"], 0)

        with self.assertRaises(ValueError):
            self.mmu.use(ptr)

    def test_kill(self):
        self.mmu.new(1, 500)
        self.mmu.new(1, 5000)

        self.mmu.kill(1)

        self.assertEqual(self.mmu.get_stats()["ram_used_kb"], 0)
        self.assertEqual(self.mmu.get_stats()["active_processes"], 0)

        with self.assertRaises(ValueError):
            self.mmu.new(1, 100)

    def test_unique_pointers(self):
        first = self.mmu.new(1, 100)
        self.mmu.delete(first)

        second = self.mmu.new(1, 100)

        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
