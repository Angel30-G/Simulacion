from math import ceil

from algorithms.fifo import FIFO
from core.models import PAGE_SIZE, RAM_FRAMES, Page, Pointer, Process


class MMU:
    def __init__(self, algorithm=None):
        self.ram: list[Page | None] = [None] * RAM_FRAMES
        self.processes: dict[int, Process] = {}
        self.pointers: dict[int, Pointer] = {}

        self.next_ptr = 1
        self.next_page_id = 1

        # Permite sustituir FIFO por otros algoritmos después.
        self.algorithm = algorithm if algorithm is not None else FIFO()

        self.clock = 0
        self.page_hits = 0
        self.page_faults = 0
        self.thrashing_time = 0

    def _get_free_frame(self):
        for frame, page in enumerate(self.ram):
            if page is None:
                return frame
        return None

    def _get_process(self, pid):
        if pid not in self.processes:
            self.processes[pid] = Process(pid=pid)

        process = self.processes[pid]

        if not process.active:
            raise ValueError(f"El proceso {pid} ya finalizo")

        return process

    def _find_resident_page(self, page_id):
        for page in self.ram:
            if page is not None and page.page_id == page_id:
                return page
        return None

    def _select_victim(self, protected=None):
        """
        Busca una pagina reemplazable sin seleccionar
        las paginas protegidas por la operacion actual.
        """
        protected = protected or set()

        for page_id in self.algorithm.get_queue():
            if page_id in protected:
                continue

            page = self._find_resident_page(page_id)

            if page is not None:
                self.algorithm.remove_page(page_id)
                return page

        raise MemoryError(
            "No hay paginas disponibles para reemplazar"
        )

    def _load_page(self, page, protected=None):
        """Carga una pagina en RAM aplicando reemplazo."""
        if page.in_ram:
            return

        frame = self._get_free_frame()

        if frame is None:
            victim = self._select_victim(protected)

            frame = victim.frame

            # La pagina reemplazada permanece en
            # el sistema, pero pasa a memoria virtual.
            victim.in_ram = False
            victim.frame = None

            self.ram[frame] = None

        page.frame = frame
        page.in_ram = True
        page.arrival_time = self.clock

        self.ram[frame] = page
        self.algorithm.add_page(page.page_id)

        # Las paginas nuevas y recuperadas son fallos.
        self.page_faults += 1
        self.clock += 5
        self.thrashing_time += 5

    def new(self, pid, size):
        """Crea un puntero y asigna sus paginas."""
        if size <= 0:
            raise ValueError("El tamaño debe ser positivo")

        process = self._get_process(pid)

        ptr = self.next_ptr
        self.next_ptr += 1

        pointer = Pointer(
            ptr=ptr,
            pid=pid,
            size=size
        )

        self.pointers[ptr] = pointer
        process.pointers[ptr] = pointer

        pages_needed = ceil(size / PAGE_SIZE)

        for _ in range(pages_needed):
            page = Page(
                page_id=self.next_page_id,
                pid=pid,
                ptr=ptr
            )

            self.next_page_id += 1
            pointer.pages.append(page)

            self._load_page(page)

        return ptr

    def use(self, ptr):
        """Accede a las paginas del puntero."""
        if ptr not in self.pointers:
            raise ValueError(f"El puntero {ptr} no existe")

        pointer = self.pointers[ptr]

        if len(pointer.pages) > RAM_FRAMES:
            raise MemoryError(
                "Pendiente definir accesos a punteros "
                "mayores que la RAM disponible"
            )

        # Protegemos las paginas del puntero que
        # ya se encuentran residentes.
        protected = {
            page.page_id
            for page in pointer.pages
            if page.in_ram
        }

        for page in pointer.pages:
            if page.in_ram:
                self.page_hits += 1
                self.clock += 1
            else:
                self._load_page(page, protected)

            protected.add(page.page_id)

            page.reference_bit = True
            page.frequency += 1
            page.last_used = self.clock

    def delete(self, ptr):
        """Libera todas las paginas del puntero."""
        if ptr not in self.pointers:
            raise ValueError(f"El puntero {ptr} no existe")

        pointer = self.pointers.pop(ptr)

        for page in pointer.pages:
            if page.in_ram:
                self.ram[page.frame] = None
                self.algorithm.remove_page(page.page_id)

            page.frame = None
            page.in_ram = False

        process = self.processes[pointer.pid]
        del process.pointers[ptr]

    def kill(self, pid):
        """Finaliza un proceso y libera sus recursos."""
        if pid not in self.processes:
            raise ValueError(f"El proceso {pid} no existe")

        process = self.processes[pid]

        if not process.active:
            raise ValueError(f"El proceso {pid} ya finalizo")

        for ptr in list(process.pointers):
            self.delete(ptr)

        process.active = False

    def get_stats(self):
        """Devuelve las estadisticas de memoria."""
        used_frames = sum(
            page is not None for page in self.ram
        )

        virtual_pages = sum(
            not page.in_ram
            for pointer in self.pointers.values()
            for page in pointer.pages
        )

        fragmentation = sum(
            ceil(pointer.size / PAGE_SIZE) * PAGE_SIZE
            - pointer.size
            for pointer in self.pointers.values()
        )

        active_processes = sum(
            process.active
            for process in self.processes.values()
        )

        return {
            "active_processes": active_processes,
            "ram_used_kb": used_frames * 4,
            "ram_percentage": used_frames / RAM_FRAMES * 100,
            "virtual_ram_kb": virtual_pages * 4,
            "virtual_ram_percentage": (
                virtual_pages / RAM_FRAMES * 100
            ),
            "clock": self.clock,
            "page_hits": self.page_hits,
            "page_faults": self.page_faults,
            "thrashing_time": self.thrashing_time,
            "thrashing_percentage": (
                self.thrashing_time / self.clock * 100
                if self.clock > 0 else 0
            ),
            "fragmentation_bytes": fragmentation
        }
