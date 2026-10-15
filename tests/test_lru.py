
from algorithms.lru import LRU
from core.mmu import MMU


def test_lru_replacement():
    mmu = MMU(algorithm=LRU())

    for i in range(100):
        mmu.new(1, 4096)

    mmu.use(1)

    mmu.new(1, 4096)

    assert mmu.pointers[1].pages[0].in_ram
    assert not mmu.pointers[2].pages[0].in_ram
    assert mmu.pointers[101].pages[0].in_ram
