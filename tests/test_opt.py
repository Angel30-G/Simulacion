from algorithms.opt import OPT
from core.models import Page


def test_opt_replacement():
    opt = OPT()

    pagina1 = Page(page_id=1, pid=1, ptr=1)
    pagina2 = Page(page_id=2, pid=1, ptr=2)
    pagina3 = Page(page_id=3, pid=1, ptr=3)

    ram = [pagina1, pagina2, pagina3]

    operaciones = [
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("use", [1]),
        ("use", [3]),
        ("use", [2]),
        ("use", [1])
    ]

    opt.set_operations(operaciones)
    opt.set_current_index(2)

    # Se reemplaza la pagina que se usara mas tarde
    assert opt.select_victim(ram) == 2


def test_opt_without_future_use():
    opt = OPT()

    pagina1 = Page(page_id=1, pid=1, ptr=1)
    pagina2 = Page(page_id=2, pid=1, ptr=2)

    ram = [pagina1, pagina2]

    operaciones = [
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("use", [1])
    ]

    opt.set_operations(operaciones)
    opt.set_current_index(1)

    # La pagina 2 no vuelve a utilizarse
    assert opt.select_victim(ram) == 2


def test_opt_protected_pages():
    opt = OPT()

    pagina1 = Page(page_id=1, pid=1, ptr=1)
    pagina2 = Page(page_id=2, pid=1, ptr=2)
    pagina3 = Page(page_id=3, pid=1, ptr=3)

    ram = [pagina1, pagina2, pagina3]

    operaciones = [
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("use", [1]),
        ("use", [3]),
        ("use", [2]),
        ("use", [1])
    ]

    opt.set_operations(operaciones)
    opt.set_current_index(2)

    # La pagina 2 se protege y no se puede reemplazar
    protegidas = {2}

    assert opt.select_victim(ram, protegidas) == 3


def test_opt_deleted_pointer():
    opt = OPT()

    pagina1 = Page(page_id=1, pid=1, ptr=1)
    pagina2 = Page(page_id=2, pid=1, ptr=2)
    pagina3 = Page(page_id=3, pid=1, ptr=3)

    ram = [pagina1, pagina2, pagina3]

    operaciones = [
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("new", [1, 4096]),
        ("use", [1]),
        ("delete", [2]),
        ("use", [3]),
        ("use", [1])
    ]

    opt.set_operations(operaciones)
    opt.set_current_index(2)

    # El puntero 2 se elimina y no se vuelve a utilizar
    assert opt.select_victim(ram) == 2


def test_opt_multiple_pages():
    opt = OPT()

    pagina1 = Page(page_id=1, pid=1, ptr=1)
    pagina2 = Page(page_id=2, pid=1, ptr=1)
    pagina3 = Page(page_id=3, pid=1, ptr=2)

    ram = [pagina1, pagina2, pagina3]

    operaciones = [
        ("new", [1, 10000]),
        ("new", [1, 4096]),
        ("use", [1]),
        ("use", [2]),
        ("use", [1])
    ]

    opt.set_operations(operaciones)
    opt.set_current_index(1)

    # Las dos primeras paginas pertenecen al mismo puntero
    assert opt.select_victim(ram) == 3
