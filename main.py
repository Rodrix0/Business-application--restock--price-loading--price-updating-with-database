import sys
from PyQt5.QtWidgets import QApplication
from windows.select_window import SelectWindow
from PyQt5.QtCore import QFile

def load_theme(app: QApplication) -> None:
    try:
        file = QFile('styles/theme.qss')
        if file.exists() and file.open(QFile.ReadOnly | QFile.Text):
            style = str(file.readAll(), encoding='utf-8')
            app.setStyleSheet(style)
    except Exception:
        # En caso de error, no interrumpimos la app; sigue con estilo por defecto
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_theme(app)
    selector = SelectWindow()
    selector.show()
    sys.exit(app.exec_()) 