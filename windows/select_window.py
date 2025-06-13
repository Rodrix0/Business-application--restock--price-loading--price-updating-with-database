from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from .main_window import MainWindow

class SelectWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar Modo")
        self.setGeometry(100, 100, 300, 200)
        self.venta = []
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.label = QLabel("¿Deseas trabajar con una o dos ventanas?")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.una_ventana_btn = QPushButton("Una ventana")
        self.una_ventana_btn.clicked.connect(self.abrir_una_ventana)
        self.layout.addWidget(self.una_ventana_btn)

        self.dos_ventanas_btn = QPushButton("Dos ventanas")
        self.dos_ventanas_btn.clicked.connect(self.abrir_dos_ventanas)
        self.layout.addWidget(self.dos_ventanas_btn)

        self.setLayout(self.layout)

    def abrir_una_ventana(self):
        self.main_window = MainWindow()  # Crear ventana principal
        self.main_window.show()
        self.close()  # Cerrar la ventana de selección

    def abrir_dos_ventanas(self):
        self.main_window1 = MainWindow()  # Crear primera ventana principal
        self.main_window2 = MainWindow()  # Crear segunda ventana principal
        self.main_window1.show()
        self.main_window2.show()
        self.close()  # Cerrar la ventana de selección 