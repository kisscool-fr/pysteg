import sys

from PyQt6.QtWidgets import QApplication

from app.gui.app_icon import apply_app_icon
from app.gui.app_icon import prepare_platform
from app.gui.main_window import MainWindow
from app.gui.ui import styles


def main():
    prepare_platform()
    app = QApplication(sys.argv)
    styles.apply_app_theme(app)
    apply_app_icon(app)

    window = MainWindow()
    apply_app_icon(app, window)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
