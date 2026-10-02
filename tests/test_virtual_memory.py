import unittest

from core.mmu import MMU
from core.models import PAGE_SIZE, RAM_FRAMES


class TestVirtualMemory(unittest.TestCase):

    def setUp(self):
        self.mmu = MMU()

    def test_fifo_replacement(self):
        first = self.mmu.new(1, PAGE_SIZE * RAM_FRAMES)

        # Esta asignacion obliga a reemplazar una pagina.
        second = self.mmu.new(2, PAGE_SIZE)

        first_page = self.mmu.pointers[first].pages[0]
        second_page = self.mmu.pointers[second].pages[0]

        self.assertFalse(first_page.in_ram)
        self.assertTrue(second_page.in_ram)

        stats = self.mmu.get_stats()

        self.assertEqual(stats["ram_used_kb"], 400)
        self.assertEqual(stats["virtual_ram_kb"], 4)
        self.assertEqual(stats["page_faults"], 101)
        self.assertEqual(stats["clock"], 505)

    def test_recover_virtual_page(self):
        first = self.mmu.new(1, PAGE_SIZE * RAM_FRAMES)
        second = self.mmu.new(2, PAGE_SIZE)

        # Se recupera la pagina faltante del primer puntero.
        self.mmu.use(first)

        self.assertTrue(
            all(
                page.in_ram
                for page in self.mmu.pointers[first].pages
            )
        )

        self.assertFalse(
            self.mmu.pointers[second].pages[0].in_ram
        )

        stats = self.mmu.get_stats()

        self.assertEqual(stats["page_hits"], 99)
        self.assertEqual(stats["page_faults"], 102)
        self.assertEqual(stats["clock"], 609)

    def test_delete_virtual_pages(self):
        first = self.mmu.new(1, PAGE_SIZE * RAM_FRAMES)
        self.mmu.new(2, PAGE_SIZE)

        self.mmu.delete(first)

        stats = self.mmu.get_stats()

        self.assertEqual(stats["ram_used_kb"], 4)
        self.assertEqual(stats["virtual_ram_kb"], 0)

    def test_kill_releases_virtual_pages(self):
        self.mmu.new(1, PAGE_SIZE * RAM_FRAMES)
        self.mmu.new(1, PAGE_SIZE)

        self.mmu.kill(1)

        stats = self.mmu.get_stats()

        self.assertEqual(stats["ram_used_kb"], 0)
        self.assertEqual(stats["virtual_ram_kb"], 0)
        self.assertEqual(stats["active_processes"], 0)


if __name__ == "__main__":
    unittest.main()
