
from algorithms.lfu import LFU
from core.mmu import MMU


def test_lfu_replacement():
    mmu = MMU(algorithm=LFU())

    # Se llena la memoria con 100 paginas
    for i in range(100):
        mmu.new(1, 4096)

    # Se utiliza la pagina 1 varias veces
    for i in range(3):
        mmu.use(1)

    mmu.use(2)

    # Se agrega otra pagina para provocar un reemplazo
    mmu.new(1, 4096)

    assert mmu.pointers[1].pages[0].in_ram
    assert mmu.pointers[2].pages[0].in_ram
    assert not mmu.pointers[3].pages[0].in_ram
    assert mmu.pointers[101].pages[0].in_ram
