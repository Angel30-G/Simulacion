from core.simulator import Simulator


def test_simulator():
    operaciones = [
        ("new", [1, 500]),
        ("new", [1, 1000]),
        ("use", [1]),
        ("use", [2]),
        ("delete", [1]),
        ("kill", [1])
    ]

    simulador = Simulator(operaciones, "LRU")

    # Se ejecutan las operaciones en ambas MMU
    simulador.run()

    assert simulador.current_index == len(operaciones)

    stats = simulador.get_stats()

    assert stats["OPT"]["page_faults"] == stats["USER"]["page_faults"]
    assert stats["OPT"]["ram_used_kb"] == 0
    assert stats["USER"]["ram_used_kb"] == 0

    assert not simulador.opt_mmu.processes[1].active
    assert not simulador.user_mmu.processes[1].active


def test_simulator_replacement():
    operaciones = []

    # Se llena la memoria con 100 paginas
    for i in range(100):
        operaciones.append(("new", [1, 4096]))

    operaciones.append(("use", [1]))
    operaciones.append(("new", [1, 4096]))
    operaciones.append(("use", [2]))
    operaciones.append(("use", [1]))

    simulador = Simulator(operaciones, "LRU")
    simulador.run()

    # Se comprueba que ambas simulaciones terminaron
    assert simulador.current_index == len(operaciones)

    assert simulador.opt_mmu.get_stats()["ram_used_kb"] == 400
    assert simulador.user_mmu.get_stats()["ram_used_kb"] == 400

    assert simulador.opt_mmu.pointers[1].pages[0].in_ram
    assert simulador.user_mmu.pointers[1].pages[0].in_ram


def test_opt_vs_lru():
    operaciones = []

    # Se llena la RAM con 100 paginas
    for i in range(100):
        operaciones.append(("new", [1, 4096]))

    operaciones.append(("use", [1]))
    operaciones.append(("new", [1, 4096]))
    operaciones.append(("use", [2]))
    operaciones.append(("use", [3]))

    simulador = Simulator(operaciones, "LRU")
    simulador.run()

    opt = simulador.opt_mmu.get_stats()
    lru = simulador.user_mmu.get_stats()

    # Se comparan los fallos que tuvo cada algoritmo
    assert opt["page_faults"] <= lru["page_faults"]
    assert simulador.current_index == len(operaciones)


def test_simulator_state():
    operaciones = [
        ("new", [1, 500]),
        ("new", [1, 10000]),
        ("use", [1])
    ]

    simulador = Simulator(operaciones, "LRU")
    simulador.run()

    estado = simulador.get_state(simulador.user_mmu)

    # Se comprueba que los datos de memoria sean correctos
    assert len(estado["frames"]) == 100
    assert len(estado["pages"]) == 4
    assert estado["ram_kb"] == 16
    assert estado["processes"] == 1
    assert estado["time"] == 21
