from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QLineEdit, QPushButton, QFileDialog,
                             QSpinBox, QGroupBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt

from operations.generator import generate_scenario
from operations.parser import parse_operations_file


class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.operations = []          # lista de tuplas: ("new", [1, 500]) ...
        self.sim_window = None
        self.setWindowTitle("Simulador de Paginación - Configuración")
        self.setMinimumSize(580, 640)
        self._build_ui()
        self._apply_style()

    # ---------- UI ----------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("Simulador de Paginación")
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel("Configure el escenario y el algoritmo a comparar contra OPT")
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        # ---- Configuración ----
        cfg = QGroupBox("Configuración")
        form = QFormLayout(cfg)
        form.setSpacing(12)

        self.seed_input = QSpinBox()
        self.seed_input.setRange(0, 999999)
        self.seed_input.setValue(42)
        form.addRow("Semilla (random):", self.seed_input)

        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["FIFO", "SC", "LRU", "LFU"])
        form.addRow("Algoritmo a simular:", self.algo_combo)

        file_row = QHBoxLayout()
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("(opcional) Ruta al archivo de operaciones...")
        self.file_btn = QPushButton("Examinar")
        self.file_btn.clicked.connect(self.select_file)
        file_row.addWidget(self.file_input)
        file_row.addWidget(self.file_btn)
        form.addRow("Archivo de operaciones:", file_row)

        self.p_combo = QComboBox()
        self.p_combo.addItems(["10", "50", "100"])
        form.addRow("Número de procesos (P):", self.p_combo)

        self.n_combo = QComboBox()
        self.n_combo.addItems(["500", "1000", "5000"])
        form.addRow("Cantidad de operaciones (N):", self.n_combo)

        root.addWidget(cfg)

        # ---- Acciones ----
        actions = QGroupBox("Acciones")
        act_layout = QVBoxLayout(actions)

        row1 = QHBoxLayout()
        self.gen_btn = QPushButton("🎲  Generar escenario")
        self.gen_btn.clicked.connect(self.generate_scenario)
        self.save_btn = QPushButton("💾  Descargar archivo de operaciones")
        self.save_btn.clicked.connect(self.save_operations)
        self.save_btn.setEnabled(False)
        row1.addWidget(self.gen_btn)
        row1.addWidget(self.save_btn)
        act_layout.addLayout(row1)

        self.status_label = QLabel("Sin operaciones cargadas.")
        self.status_label.setObjectName("status")
        act_layout.addWidget(self.status_label)

        root.addWidget(actions)

        # ---- Iniciar ----
        self.start_btn = QPushButton("▶  Iniciar Simulación")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start_simulation)
        root.addWidget(self.start_btn)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2e; color: #e0e0e0;
                      font-family: 'Segoe UI','DejaVu Sans',sans-serif; font-size: 13px; }
            QLabel#title { font-size: 22px; font-weight: bold; color: #89b4fa; }
            QLabel#subtitle { color: #a6adc8; font-size: 12px; }
            QLabel#status { color: #a6adc8; font-size: 12px; }
            QGroupBox { border: 1px solid #313244; border-radius: 8px;
                        margin-top: 12px; padding-top: 12px;
                        font-weight: bold; color: #cba6f7; }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
            QLineEdit, QComboBox, QSpinBox {
                background-color: #313244; border: 1px solid #45475a;
                border-radius: 6px; padding: 6px 8px; color: #e0e0e0; }
            QPushButton { background-color: #313244; border: 1px solid #45475a;
                          border-radius: 6px; padding: 8px 14px; color: #e0e0e0; }
            QPushButton:hover { background-color: #45475a; }
            QPushButton:disabled { color: #6c7086; }
            QPushButton#startBtn { background-color: #89b4fa; color: #1e1e2e;
                                   font-weight: bold; padding: 12px; font-size: 14px; }
            QPushButton#startBtn:hover { background-color: #a6c8ff; }
        """)

    # ---------- Acciones ----------
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo de operaciones", "",
            "Archivos de operaciones (*.txt *.csv);;Todos (*)")
        if not path:
            return
        self.file_input.setText(path)
        try:
            self.operations = parse_operations_file(path)
            self.save_btn.setEnabled(True)
            self.status_label.setText(
                f"✔ Archivo cargado: {len(self.operations)} operaciones.")
        except Exception as e:
            QMessageBox.critical(self, "Error al leer archivo", str(e))

    def generate_scenario(self):
        try:
            seed = self.seed_input.value()
            p = int(self.p_combo.currentText())
            n = int(self.n_combo.currentText())
            self.operations = generate_scenario(seed, p, n)
            self.save_btn.setEnabled(True)
            self.status_label.setText(
                f"✔ Escenario generado: semilla={seed}, P={p}, N={n} "
                f"→ {len(self.operations)} operaciones.")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar escenario", str(e))

    # ===== AQUÍ VA save_operations =====
    def save_operations(self):
        if not self.operations:
            QMessageBox.warning(self, "Sin datos",
                                "Primero genere o cargue un escenario.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar archivo de operaciones",
            "operaciones.txt", "Texto (*.txt);;CSV (*.csv)")
        if not path:
            return
        try:
            with open(path, 'w', encoding='utf-8') as f:
                for op, args in self.operations:
                    f.write(f"{op}({','.join(map(str, args))})\n")
            QMessageBox.information(self, "Guardado",
                                    f"Archivo guardado en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def start_simulation(self):
        if not self.operations:
            QMessageBox.warning(self, "Sin datos",
                                "Genere o cargue un escenario primero.")
            return
        from interface.visualization import SimulationWindow
        algo = self.algo_combo.currentText()
        self.sim_window = SimulationWindow(self.operations, algo)
        self.sim_window.show()