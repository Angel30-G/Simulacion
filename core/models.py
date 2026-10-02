from dataclasses import dataclass, field

# Configuración de la computadora simulada
PAGE_SIZE = 4096
RAM_FRAMES = 100
RAM_SIZE = PAGE_SIZE * RAM_FRAMES


@dataclass
class Page:
    page_id: int
    pid: int
    ptr: int

    # Ubicación física
    frame: int | None = None
    in_ram: bool = False

    # Información para los algoritmos
    reference_bit: bool = False
    last_used: int = 0
    frequency: int = 0
    arrival_time: int = 0


@dataclass
class Pointer:
    ptr: int
    pid: int
    size: int
    pages: list[Page] = field(default_factory=list)


@dataclass
class Process:
    pid: int
    pointers: dict[int, Pointer] = field(default_factory=dict)
    active: bool = True
