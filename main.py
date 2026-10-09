import sys
from PyQt5.QtWidgets import QApplication
from interface.app import ConfigWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simulador de Paginación")
    window = ConfigWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()