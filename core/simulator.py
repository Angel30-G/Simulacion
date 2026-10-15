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
