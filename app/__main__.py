import sys

from PyQt6.QtWidgets import QApplication

from app.gui.main_window import MainWindow
from app.gui.ui import styles


def main():
    app = QApplication(sys.argv)
    styles.apply_app_theme(app)

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
