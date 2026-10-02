from math import ceil

from core.models import PAGE_SIZE, RAM_FRAMES, Page, Pointer, Process


class MMU:
    def __init__(self):
        # Cada posición representa un marco de RAM.
        self.ram: list[Page | None] = [None] * RAM_FRAMES

        # Procesos y punteros registrados.
        self.processes: dict[int, Process] = {}
        self.pointers: dict[int, Pointer] = {}

        # Los identificadores nunca se reutilizan.
        self.next_ptr = 1
        self.next_page_id = 1

        # Estadísticas de la simulación.
        self.clock = 0
        self.page_hits = 0
        self.page_faults = 0
        self.thrashing_time = 0

    def _get_free_frames(self):
        """Devuelve los números de los marcos disponibles."""
        return [
            index
            for index, page in enumerate(self.ram)
            if page is None
        ]

    def _get_process(self, pid):
        """Obtiene o registra un proceso activo."""
        if pid not in self.processes:
            self.processes[pid] = Process(pid=pid)

        process = self.processes[pid]

        if not process.active:
            raise ValueError(
                f"El proceso {pid} ya fue finalizado"
            )

        return process

    def new(self, pid, size):
        """Asigna memoria nueva a un proceso."""
        if size <= 0:
            raise ValueError("El tamaño debe ser mayor que cero")

        # Versión inicial: todavía no incorpora FIFO.
        pages_needed = ceil(size / PAGE_SIZE)
        free_frames = self._get_free_frames()

        if len(free_frames) < pages_needed:
            raise MemoryError(
                "RAM insuficiente: todavía falta implementar FIFO"
            )

        process = self._get_process(pid)

        ptr = self.next_ptr
        self.next_ptr += 1

        pointer = Pointer(
            ptr=ptr,
            pid=pid,
            size=size
        )

        for frame in free_frames[:pages_needed]:
            page = Page(
                page_id=self.next_page_id,
                pid=pid,
                ptr=ptr,
                frame=frame,
                in_ram=True
            )

            self.next_page_id += 1

            self.ram[frame] = page
            pointer.pages.append(page)

            # Las páginas nuevas siempre son fallos.
            self.page_faults += 1
            self.clock += 5
            self.thrashing_time += 5

        self.pointers[ptr] = pointer
        process.pointers[ptr] = pointer

        return ptr

    def use(self, ptr):
        """Accede a todas las páginas de un puntero."""
        if ptr not in self.pointers:
            raise ValueError(f"El puntero {ptr} no existe")

        pointer = self.pointers[ptr]

        for page in pointer.pages:
            if not page.in_ram:
                raise MemoryError(
                    "Página en memoria virtual: "
                    "todavía falta implementar FIFO"
                )

            self.page_hits += 1
            self.clock += 1

            page.reference_bit = True
            page.frequency += 1
            page.last_used = self.clock

    def delete(self, ptr):
        """Libera todas las páginas de un puntero."""
        if ptr not in self.pointers:
            raise ValueError(f"El puntero {ptr} no existe")

        pointer = self.pointers.pop(ptr)

        for page in pointer.pages:
            if page.in_ram and page.frame is not None:
                self.ram[page.frame] = None

            page.frame = None
            page.in_ram = False

        process = self.processes[pointer.pid]
        del process.pointers[ptr]

    def kill(self, pid):
        """Finaliza un proceso y libera toda su memoria."""
        if pid not in self.processes:
            raise ValueError(f"El proceso {pid} no existe")

        process = self.processes[pid]

        if not process.active:
            raise ValueError(
                f"El proceso {pid} ya fue finalizado"
            )

        for ptr in list(process.pointers):
            self.delete(ptr)

        process.active = False

    def get_stats(self):
        """Devuelve las estadísticas actuales."""
        used_frames = sum(
            page is not None for page in self.ram
        )

        # Solo se consideran las asignaciones existentes.
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
            "virtual_ram_kb": 0,
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
