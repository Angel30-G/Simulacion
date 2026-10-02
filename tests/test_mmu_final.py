import unittest

from core.mmu import MMU
from core.models import PAGE_SIZE, RAM_FRAMES


class TestMMUFinal(unittest.TestCase):

    def setUp(self):
        self.mmu = MMU()

    def test_pointer_larger_than_ram(self):
        # Crear un puntero que necesita 101 páginas.
        ptr = self.mmu.new(
            1, PAGE_SIZE * (RAM_FRAMES + 1)
        )

        stats = self.mmu.get_stats()

        self.assertEqual(
            len(self.mmu.pointers[ptr].pages), 101
        )
        self.assertEqual(stats["ram_used_kb"], 400)
        self.assertEqual(stats["virtual_ram_kb"], 4)

        # Acceder secuencialmente a sus 101 páginas.
        self.mmu.use(ptr)

        stats = self.mmu.get_stats()

        self.assertEqual(stats["ram_used_kb"], 400)
        self.assertEqual(stats["virtual_ram_kb"], 4)

        # Ninguna página debe ocupar un marco inválido.
        for page in self.mmu.pointers[ptr].pages:
            if page.in_ram:
                self.assertIsNotNone(page.frame)
                self.assertGreaterEqual(page.frame, 0)
                self.assertLess(page.frame, RAM_FRAMES)

    def test_internal_fragmentation(self):
        ptr = self.mmu.new(1, 500)

        # Se reservaron 4096 bytes para 500 bytes.
        self.assertEqual(
            self.mmu.get_stats()["fragmentation_bytes"],
            4096 - 500
        )

        self.mmu.delete(ptr)

        self.assertEqual(
            self.mmu.get_stats()["fragmentation_bytes"],
            0
        )

    def test_fifo_does_not_reorder_on_hit(self):
        first = self.mmu.new(1, PAGE_SIZE)
        second = self.mmu.new(1, PAGE_SIZE)

        # Un hit no debe modificar la antigüedad FIFO.
        self.mmu.use(first)

        self.assertEqual(
            self.mmu.algorithm.get_queue()[:2],
            [
                self.mmu.pointers[first].pages[0].page_id,
                self.mmu.pointers[second].pages[0].page_id
            ]
        )

    def test_time_and_thrashing(self):
        ptr = self.mmu.new(1, PAGE_SIZE * 2)

        # Dos páginas nuevas: dos fallos de 5 segundos.
        self.assertEqual(
            self.mmu.get_stats()["clock"], 10
        )

        self.mmu.use(ptr)

        stats = self.mmu.get_stats()

        self.assertEqual(stats["page_faults"], 2)
        self.assertEqual(stats["page_hits"], 2)
        self.assertEqual(stats["clock"], 12)
        self.assertEqual(stats["thrashing_time"], 10)

    def test_deleted_pointer_is_not_reused(self):
        first = self.mmu.new(1, PAGE_SIZE)
        self.mmu.delete(first)
        second = self.mmu.new(1, PAGE_SIZE)

        self.assertGreater(second, first)


if __name__ == "__main__":
    unittest.main()
