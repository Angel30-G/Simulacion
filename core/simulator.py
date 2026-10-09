from PyQt5.QtCore import QTimer

class SimulationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.paused = False
        self.current_index = 0
        # ...

    def start_simulation(self):
        self.timer.start(100)  # 100 ms por paso

    def step(self):
        if self.current_index >= len(self.operations):
            self.timer.stop()
            return
        # Ejecutar una operación en ambos simuladores
        self.opt_mmu.execute(self.operations[self.current_index])
        self.user_mmu.execute(self.operations[self.current_index])
        self.current_index += 1
        self.update_visualization()

    def pause(self):
        self.timer.stop()
        self.paused = True

    def resume(self):
        if self.paused:
            self.timer.start(100)
            self.paused = False