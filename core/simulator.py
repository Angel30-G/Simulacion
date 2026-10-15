from core.mmu import MMU
from algorithms.fifo import FIFO
from algorithms.lru import LRU
from algorithms.lfu import LFU
from algorithms.second_chance import SecondChance
from algorithms.opt import OPT


class Simulator:
    def __init__(self, operations, algorithm):
        self.operations = operations
        self.current_index = 0

        self.opt = OPT()
        self.opt.set_operations(operations)

        if algorithm == "FIFO":
            self.user_algorithm = FIFO()
        elif algorithm == "LRU":
            self.user_algorithm = LRU()
        elif algorithm == "LFU":
            self.user_algorithm = LFU()
        elif algorithm == "SC":
            self.user_algorithm = SecondChance()
        else:
            raise ValueError("Algoritmo no valido")

        self.opt_mmu = MMU(self.opt)
        self.user_mmu = MMU(self.user_algorithm)

    def execute_operation(self, mmu, operation):
        op, args = operation

        if op == "new":
            mmu.new(args[0], args[1])
        elif op == "use":
            mmu.use(args[0])
        elif op == "delete":
            mmu.delete(args[0])
        elif op == "kill":
            mmu.kill(args[0])
        else:
            raise ValueError("Operacion no valida")

    def step(self):
        if self.current_index >= len(self.operations):
            return False

        # Se ejecuta la misma operacion en las dos MMU
        operation = self.operations[self.current_index]

        self.opt.set_current_index(self.current_index)

        self.execute_operation(self.opt_mmu, operation)
        self.execute_operation(self.user_mmu, operation)

        self.current_index += 1
        return True

    def run(self):
        while self.step():
            pass

    def get_stats(self):
        return {
            "OPT": self.opt_mmu.get_stats(),
            "USER": self.user_mmu.get_stats()
        }

    def reset(self):
        self.__init__(self.operations, self.get_algorithm_name())

    def get_algorithm_name(self):
        if isinstance(self.user_algorithm, FIFO):
            return "FIFO"
        elif isinstance(self.user_algorithm, LRU):
            return "LRU"
        elif isinstance(self.user_algorithm, LFU):
            return "LFU"
        elif isinstance(self.user_algorithm, SecondChance):
            return "SC"


    def get_state(self, mmu):
        stats = mmu.get_stats()

        
        colores = [
            "#f38ba8", "#fab387", "#f9e2af", "#a6e3a1",
            "#94e2d5", "#89dceb", "#89b4fa", "#b4befe",
            "#cba6f7", "#f5c2e7", "#eba0ac", "#74c7ec"
        ]

        frames = []
        for page in mmu.ram:
            if page is None:
                frames.append(None)
            else:
                color = colores[(page.pid - 1) % len(colores)]
                frames.append((page.pid, page.page_id, color))


        pages = []
        for pointer in mmu.pointers.values():
            for page in pointer.pages:
                pages.append({
                    "page_id": page.page_id,
                    "pid": page.pid,
                    "loaded": page.in_ram,
                    "l_addr": page.ptr,
                    "m_addr": page.frame if page.in_ram else "",
                    "d_addr": "" if page.in_ram else page.page_id,
                    "loaded_t": page.arrival_time
                })

        # Se preparan los datos que necesita la interfaz
        return {
            "frames": frames,
            "pages": pages,
            "time": stats["clock"],
            "processes": stats["active_processes"],
            "ram_kb": stats["ram_used_kb"],
            "ram_pct": round(stats["ram_percentage"], 1),
            "vram_kb": stats["virtual_ram_kb"],
            "vram_pct": round(stats["virtual_ram_percentage"], 1),
            "thrash_s": stats["thrashing_time"],
            "thrash_pct": round(stats["thrashing_percentage"], 1),
            "frag_kb": round(stats["fragmentation_bytes"] / 1024, 2)
        }
