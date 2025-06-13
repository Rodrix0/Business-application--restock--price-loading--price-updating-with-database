import sys
from PyQt5.QtWidgets import QApplication
from windows.select_window import SelectWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    selector = SelectWindow()
    selector.show()
    sys.exit(app.exec_()) 