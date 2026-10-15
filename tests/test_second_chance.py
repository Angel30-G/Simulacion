from algorithms.second_chance import SecondChance
from core.mmu import MMU


def test_second_chance_replacement():
    mmu = MMU(algorithm=SecondChance())

    # Se llena la memoria con 100 paginas
    for i in range(100):
        mmu.new(1, 4096)

    # Se utiliza la primera pagina para darle otra oportunidad
    mmu.use(1)

    # Se agrega una pagina nueva para provocar un reemplazo
    mmu.new(1, 4096)

    assert mmu.pointers[1].pages[0].in_ram
    assert not mmu.pointers[2].pages[0].in_ram
    assert mmu.pointers[101].pages[0].in_ram


def test_second_chance_all_referenced():
    mmu = MMU(algorithm=SecondChance())

    # Se llena la memoria con 100 paginas
    for i in range(100):
        mmu.new(1, 4096)

    # Todas las paginas se utilizan
    for i in range(1, 101):
        mmu.use(i)

    # Se agrega otra pagina para provocar un reemplazo
    mmu.new(1, 4096)

    assert not mmu.pointers[1].pages[0].in_ram
    assert mmu.pointers[101].pages[0].in_ram
    assert mmu.get_stats()["ram_used_kb"] == 400
