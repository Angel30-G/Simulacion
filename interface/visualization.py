import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGroupBox, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QBrush, QPainter, QPen


# ---------- Paleta de colores por PID ----------
PALETTE = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1",
           "#94e2d5", "#89dceb", "#89b4fa", "#b4befe",
           "#cba6f7", "#f5c2e7", "#eba0ac", "#74c7ec"]


def pid_color(pid):
    if pid is None:
        return "#313244"
    return PALETTE[(pid - 1) % len(PALETTE)]


# ---------- Barra de RAM dibujada a mano ----------
class RamBar(QWidget):
    def __init__(self, total_frames=100, parent=None):
        super().__init__(parent)
        self.total_frames = total_frames
        self.frames = [None] * total_frames
        self.setMinimumHeight(70)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_frames(self, frames):
        self.frames = frames
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        cols = 20
        rows = (self.total_frames + cols - 1) // cols
        cw = self.width() / cols
        ch = self.height() / rows
        for i in range(self.total_frames):
            r, c = divmod(i, cols)
            x, y = c * cw, r * ch
            data = self.frames[i]
            if data is None:
                p.setBrush(QBrush(QColor("#313244")))
                p.setPen(QPen(QColor("#45475a"), 1))
            else:
                _, _, color = data
                p.setBrush(QBrush(QColor(color)))
                p.setPen(QPen(QColor("#1e1e2e"), 1))
            p.drawRect(int(x) + 1, int(y) + 1, int(cw) - 2, int(ch) - 2)


# ---------- Panel de un algoritmo ----------
class AlgorithmPanel(QWidget):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.name = name
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        title = QLabel(self.name)
        title.setObjectName("panelTitle")
        lay.addWidget(title)

        lbl1 = QLabel("Memoria RAM (100 páginas × 4KB)")
        lbl1.setObjectName("sectionLabel")
        lay.addWidget(lbl1)
        self.ram_bar = RamBar(100)
        lay.addWidget(self.ram_bar)

        lbl2 = QLabel("Mapa de Memoria (MMU)")
        lbl2.setObjectName("sectionLabel")
        lay.addWidget(lbl2)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["PAGE ID", "PID", "LOADED", "L-ADDR", "M-ADDR", "D-ADDR", "LOADED T"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setMinimumHeight(240)
        lay.addWidget(self.table)

        stats = QGroupBox("Estadísticas")
        grid = QGridLayout(stats)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)

        self.lbl_time = QLabel("0 s")
        self.lbl_proc = QLabel("0")
        self.lbl_ram = QLabel("0 KB (0%)")
        self.lbl_vram = QLabel("0 KB (0% RAM)")
        self.lbl_thrash = QLabel("0 s (0%)")
        self.lbl_frag = QLabel("0 KB")

        rows = [
            ("Tiempo total:", self.lbl_time),
            ("Procesos corriendo:", self.lbl_proc),
            ("RAM usada:", self.lbl_ram),
            ("V-RAM usada:", self.lbl_vram),
            ("Thrashing:", self.lbl_thrash),
            ("Fragmentación interna:", self.lbl_frag),
        ]
        for i, (txt, val) in enumerate(rows):
            k = QLabel(txt); k.setObjectName("statKey")
            grid.addWidget(k, i, 0)
            grid.addWidget(val, i, 1)
        lay.addWidget(stats)

    def update_from_state(self, s):
        self.ram_bar.set_frames(s["frames"])

        pages = s["pages"]
        self.table.setRowCount(len(pages))
        for i, p in enumerate(pages):
            vals = [str(p["page_id"]), str(p["pid"]),
                    "X" if p["loaded"] else "",
                    str(p["l_addr"]), str(p["m_addr"]),
                    str(p["d_addr"]), str(p["loaded_t"])]
            base = QColor(pid_color(p["pid"]))
            base.setAlpha(120)
            for j, v in enumerate(vals):
                it = QTableWidgetItem(v)
                it.setBackground(QBrush(base))
                it.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, it)

        self.lbl_time.setText(f"{s['time']} s")
        self.lbl_proc.setText(str(s["processes"]))
        self.lbl_ram.setText(f"{s['ram_kb']} KB ({s['ram_pct']}%)")
        self.lbl_vram.setText(f"{s['vram_kb']} KB ({s['vram_pct']}% RAM)")
        self.lbl_thrash.setText(f"{s['thrash_s']} s ({s['thrash_pct']}%)")
        self.lbl_frag.setText(f"{s['frag_kb']} KB")

        if s["thrash_pct"] > 50:
            self.lbl_thrash.setStyleSheet("color:#f38ba8; font-weight:bold;")
        else:
            self.lbl_thrash.setStyleSheet("")


# ---------- Ventana de simulación ----------
class SimulationWindow(QWidget):
    def __init__(self, operations, user_algo):
        super().__init__()
        self.operations = operations
        self.user_algo = user_algo
        self.current_index = 0
        self.paused = False
        self.setWindowTitle(f"Simulación — OPT vs {user_algo}")
        self.setMinimumSize(1400, 900)

        self._build_ui()
        self._apply_style()
        self._load_demo_state()   # ← reemplaza cuando tengas la MMU real

        self.timer = QTimer()
        self.timer.timeout.connect(self._step)
        self.timer.start(500)

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QLabel(f"Comparación en vivo:  OPT   ⚔   {self.user_algo}")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        root.addWidget(header)

        panels = QHBoxLayout()
        panels.setSpacing(12)
        self.opt_panel = AlgorithmPanel("OPT (Óptimo)")
        self.user_panel = AlgorithmPanel(self.user_algo)
        panels.addWidget(self.opt_panel)
        panels.addWidget(self.user_panel)
        root.addLayout(panels, stretch=1)

        ctrl = QHBoxLayout()
        ctrl.addStretch()
        self.pause_btn = QPushButton("⏸  Pausar")
        self.pause_btn.clicked.connect(self._toggle_pause)
        self.step_btn = QPushButton("⏭  Paso a paso")
        self.step_btn.clicked.connect(self._step)
        self.reset_btn = QPushButton("⟲  Reiniciar")
        self.reset_btn.clicked.connect(self._reset)
        ctrl.addWidget(self.pause_btn)
        ctrl.addWidget(self.step_btn)
        ctrl.addWidget(self.reset_btn)
        ctrl.addStretch()
        root.addLayout(ctrl)

        self.progress_label = QLabel("Operación 0 / 0")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setObjectName("progress")
        root.addWidget(self.progress_label)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget { background-color:#1e1e2e; color:#e0e0e0;
                      font-family:'Segoe UI','DejaVu Sans',sans-serif; font-size:12px; }
            QLabel#header { font-size:20px; font-weight:bold; color:#89b4fa; padding:4px; }
            QLabel#panelTitle { font-size:15px; font-weight:bold; color:#cba6f7;
                                padding:4px; border-bottom:1px solid #313244; }
            QLabel#sectionLabel { color:#a6adc8; font-size:11px; margin-top:4px; }
            QLabel#statKey { color:#a6adc8; }
            QLabel#progress { color:#a6adc8; font-size:12px; }
            QGroupBox { border:1px solid #313244; border-radius:6px;
                        margin-top:10px; padding-top:10px;
                        font-weight:bold; color:#cba6f7; }
            QGroupBox::title { subcontrol-origin:margin; left:8px; padding:0 4px; }
            QTableWidget { background-color:#181825; border:1px solid #313244;
                           gridline-color:#313244; color:#e0e0e0; }
            QHeaderView::section { background-color:#313244; color:#e0e0e0;
                                   border:none; padding:4px; font-weight:bold; }
            QPushButton { background-color:#313244; border:1px solid #45475a;
                          border-radius:6px; padding:8px 18px; color:#e0e0e0;
                          font-weight:bold; }
            QPushButton:hover { background-color:#45475a; }
        """)

    # -------- Controles --------
    def _toggle_pause(self):
        if self.paused:
            self.timer.start(500)
            self.pause_btn.setText("⏸  Pausar")
            self.paused = False
        else:
            self.timer.stop()
            self.pause_btn.setText("▶  Reanudar")
            self.paused = True

    def _step(self):
        if not self.operations:
            return
        if self.current_index >= len(self.operations):
            self.timer.stop()
            self.progress_label.setText("Simulación completa ✔")
            return

        # ====== INTEGRACIÓN REAL (cuando tengas los algoritmos) ======
        # instr = self.operations[self.current_index]
        # self.opt_mmu.execute(instr)
        # self.user_mmu.execute(instr)
        # self.opt_panel.update_from_state(self._snapshot(self.opt_mmu))
        # self.user_panel.update_from_state(self._snapshot(self.user_mmu))
        # =============================================================

        self.current_index += 1
        op, args = self.operations[self.current_index - 1]
        self.progress_label.setText(
            f"Operación {self.current_index} / {len(self.operations)}   →   "
            f"{op}({','.join(map(str,args))})")
        self._load_demo_state()

    def _reset(self):
        self.current_index = 0
        self.timer.stop()
        self.paused = False
        self.pause_btn.setText("⏸  Pausar")
        self._load_demo_state()
        self.timer.start(500)

    # -------- Datos demo (borrar cuando integres la MMU real) --------
    def _load_demo_state(self):
        rng = random.Random(self.current_index)
        def make(offset=0):
            frames = []
            for i in range(100):
                if rng.random() < 0.55:
                    pid = rng.randint(1, 8)
                    frames.append((pid, i + 1 + offset, pid_color(pid)))
                else:
                    frames.append(None)
            pages = []
            for i in range(rng.randint(6, 14)):
                pid = rng.randint(1, 8)
                pages.append({
                    "page_id": i + 1 + offset, "pid": pid,
                    "loaded": rng.random() < 0.7,
                    "l_addr": rng.randint(1, 999),
                    "m_addr": rng.randint(0, 99),
                    "d_addr": rng.randint(0, 999),
                    "loaded_t": rng.randint(0, 100),
                })
            ram_kb = sum(1 for f in frames if f) * 4
            t = self.current_index * 3
            thr = max(0, t - rng.randint(0, 20))
            return {
                "frames": frames, "pages": pages, "time": t,
                "processes": rng.randint(1, 8),
                "ram_kb": ram_kb,
                "ram_pct": round(ram_kb / 400 * 100, 1),
                "vram_kb": rng.randint(0, 800),
                "vram_pct": rng.randint(0, 200),
                "thrash_s": thr,
                "thrash_pct": round(thr / max(1, t) * 100, 1) if t else 0,
                "frag_kb": rng.randint(0, 50),
            }
        self.opt_panel.update_from_state(make(0))
        self.user_panel.update_from_state(make(100))