from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QMessageBox, QInputDialog, QComboBox, QListWidget, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from datetime import date
from db import conectar_db
from voice.voice_thread import VoiceRecognitionThread
from utils.price_utils import correccion_precio

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.venta = []
        self.initUI()

    def initUI(self):
        self.label_imagen = QLabel(self)
        pixmap = QPixmap("./img/Foto.png")
        pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio)
        self.label_imagen.setPixmap(pixmap)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label_imagen, alignment=Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(self.layout)
        self.setWindowTitle('Imagen en esquina superior izquierda')
        self.resize(400, 300)
        # Etiqueta de bienvenida
        self.label = QLabel("¡Bienvenido a ")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.layout.addWidget(self.label)
        # Botón de ingresar
        self.ingresar_btn = QPushButton("Ingresar")
        self.ingresar_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.ingresar_btn.clicked.connect(self.mostrar_pantalla_opciones)
        self.layout.addWidget(self.ingresar_btn)
        self.setLayout(self.layout)

    def mostrar_pantalla_opciones(self):
        self.limpiar_layout()
        self.label_opciones = QLabel("Seleccione una opción")
        self.label_opciones.setAlignment(Qt.AlignCenter)
        self.label_opciones.setStyleSheet("font-size: 20px; background-color: white; color: black;")
        self.layout.addWidget(self.label_opciones)
        self.insertar_btn = QPushButton("Insertar/Actualizar Producto")
        self.insertar_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.insertar_btn.clicked.connect(self.mostrar_pantalla_insertar)
        self.layout.addWidget(self.insertar_btn)
        self.vender_btn = QPushButton("Vender Producto")
        self.vender_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.vender_btn.clicked.connect(self.mostrar_pantalla_vender)
        self.layout.addWidget(self.vender_btn)
        self.eliminar_btn = QPushButton("Lista de Restock")
        self.eliminar_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.eliminar_btn.clicked.connect(self.mostrar_pantalla_restock)
        self.layout.addWidget(self.eliminar_btn)
        self.ver_ventas_btn = QPushButton("Ver Ventas del Día")
        self.ver_ventas_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.ver_ventas_btn.clicked.connect(self.mostrar_pantalla_ventas)
        self.layout.addWidget(self.ver_ventas_btn)

    def limpiar_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def mostrar_pantalla_vender(self):    
        self.limpiar_layout()
        self.label_vender = QLabel("Vender Producto")
        self.label_vender.setAlignment(Qt.AlignCenter)
        self.label_vender.setStyleSheet("font-size: 20px; background-color: white; color: black;")
        self.layout.addWidget(self.label_vender)
        self.entry_buscar_vender = QLineEdit(self)
        self.entry_buscar_vender.setPlaceholderText("Buscar Producto")
        self.entry_buscar_vender.setStyleSheet("font-size: 20px;")
        self.entry_buscar_vender.returnPressed.connect(self.buscar_producto)
        self.entry_buscar_vender.editingFinished.connect(self.buscar_producto)
        self.layout.addWidget(self.entry_buscar_vender)
        self.treeview_vender = QTableWidget()
        self.treeview_vender.setColumnCount(3)
        self.treeview_vender.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Precio"])
        self.treeview_vender.setSelectionBehavior(QTableWidget.SelectRows)
        self.treeview_vender.setSelectionMode(QTableWidget.SingleSelection)
        self.treeview_vender.cellClicked.connect(self.seleccionar_producto)
        self.layout.addWidget(self.treeview_vender)
        self.manual_btn = QPushButton("Ingresar Precio Manual")
        self.manual_btn.setStyleSheet("font-size: 15px;")
        self.manual_btn.clicked.connect(self.ingresar_precio_manual)
        self.layout.addWidget(self.manual_btn)
        self.label_metodo_pago = QLabel("Método de Pago:")
        self.label_metodo_pago.setStyleSheet("font-size: 15px;")
        self.layout.addWidget(self.label_metodo_pago)
        self.combo_metodo_pago = QComboBox(self)
        self.combo_metodo_pago.addItems(["Efectivo", "Mercado Pago"])
        self.combo_metodo_pago.setStyleSheet("font-size: 15px;")
        self.combo_metodo_pago.currentIndexChanged.connect(self.on_metodo_pago_changed)
        self.layout.addWidget(self.combo_metodo_pago)
        self.btn_confirmar_pago = QPushButton("Confirmar Método de Pago", self)
        self.btn_confirmar_pago.setStyleSheet("font-size: 15px;")
        self.btn_confirmar_pago.setEnabled(False)
        self.btn_confirmar_pago.clicked.connect(self.mostrar_qr_mercado_pago)
        self.layout.addWidget(self.btn_confirmar_pago)
        self.label_lista_venta = QLabel("Lista de Venta")
        self.label_lista_venta.setAlignment(Qt.AlignCenter)
        self.label_lista_venta.setStyleSheet("font-size: 15px;")
        self.layout.addWidget(self.label_lista_venta)
        self.treeview_lista_venta = QTableWidget()
        self.treeview_lista_venta.setColumnCount(4)
        self.treeview_lista_venta.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Precio", "Total"])
        self.layout.addWidget(self.treeview_lista_venta)
        self.label_total = QLabel("Total: $0.00")
        self.label_total.setStyleSheet("font-size: 30px;")
        self.layout.addWidget(self.label_total)
        self.eliminar_btn = QPushButton("Eliminar de la Lista")
        self.eliminar_btn.setStyleSheet("font-size: 15px; background-color: red; color: black;")
        self.eliminar_btn.clicked.connect(self.eliminar_producto_lista)
        self.layout.addWidget(self.eliminar_btn)
        self.confirmar_venta_btn = QPushButton("Confirmar Venta")
        self.confirmar_venta_btn.setStyleSheet("font-size: 15px; background-color: red; color: black;")
        self.confirmar_venta_btn.clicked.connect(self.confirmar_venta)
        self.layout.addWidget(self.confirmar_venta_btn)
        self.volver_btn = QPushButton("Volver")
        self.volver_btn.setStyleSheet("font-size: 15px; background-color: red; color: black;")
        self.volver_btn.clicked.connect(self.mostrar_pantalla_opciones)
        self.layout.addWidget(self.volver_btn)
        self.buscar_producto()  # Mostrar todos los productos al abrir la pantalla

    def confirmar_venta(self):
        if not self.venta:
            QMessageBox.warning(self, "Advertencia", "No hay productos en la lista de venta.")
            return
        metodo_pago = self.combo_metodo_pago.currentText()
        if metodo_pago == "Efectivo":
            self.procesar_venta_efectivo()
        elif metodo_pago == "Mercado Pago":
            self.procesar_venta_mercado_pago()
        self.buscar_producto()  # Actualizar la tabla de productos después de la venta

    def on_metodo_pago_changed(self):
        metodo_seleccionado = self.combo_metodo_pago.currentText()
        if metodo_seleccionado == "Mercado Pago":
            self.btn_confirmar_pago.setEnabled(True)
        else:
            self.btn_confirmar_pago.setEnabled(False)

    def mostrar_qr_mercado_pago(self):
        self.ventana_qr = QDialog(self)
        self.ventana_qr.setWindowTitle("Pago con Mercado Pago")
        self.ventana_qr.setModal(True)
        layout = QVBoxLayout()
        label_qr = QLabel()
        pixmap = QPixmap("./img/qr.png")
        if pixmap.isNull():
            print("Error: No se pudo cargar la imagen QR. Verifica la ruta del archivo.")
        else:
            label_qr.setPixmap(pixmap)
            layout.addWidget(label_qr)
        self.ventana_qr.setLayout(layout)
        self.ventana_qr.exec_()

    def procesar_venta_efectivo(self):
        db = conectar_db()
        cursor = db.cursor()
        for item in self.venta:
            nombre = item[0]
            cantidad = item[1]
            total = item[3]
            insert_query = "INSERT INTO ventas (fecha, nombre, cantidad, total) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (date.today(), nombre, cantidad, total))
            update_query = "UPDATE productos SET cantidad = cantidad - %s WHERE nombre = %s"
            cursor.execute(update_query, (cantidad, nombre))
        db.commit()
        cursor.close()
        db.close()
        QMessageBox.information(self, "Éxito", "Venta confirmada.")
        self.venta.clear()
        self.actualizar_lista_venta()

    def procesar_venta_mercado_pago(self):
        db = conectar_db()
        cursor = db.cursor()
        for item in self.venta:
            nombre = item[0]
            cantidad = item[1]
            total = item[3]
            insert_query = "INSERT INTO ventas (fecha, nombre, cantidad, total) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (date.today(), nombre, cantidad, total))
            update_query = "UPDATE productos SET cantidad = cantidad - %s WHERE nombre = %s"
            cursor.execute(update_query, (cantidad, nombre))
        db.commit()
        cursor.close()
        db.close()
        QMessageBox.information(self, "Éxito", "Venta confirmada.")
        self.venta.clear()
        self.actualizar_lista_venta()
        self.ventana_qr.close()

    def mostrar_pantalla_insertar(self):
        self.limpiar_layout()
        self.label_insertar = QLabel("Insertar o Actualizar Producto")
        self.label_insertar.setAlignment(Qt.AlignCenter)
        self.label_insertar.setStyleSheet("font-size: 20px; background-color: white; color: black;")
        self.layout.addWidget(self.label_insertar)
        self.lista_productos = QListWidget(self)
        self.lista_productos.setStyleSheet("font-size: 16px;")
        self.lista_productos.itemClicked.connect(self.cargar_producto_seleccionado)
        self.layout.addWidget(self.lista_productos)
        productos = self.obtener_productos()
        for producto in productos:
            self.lista_productos.addItem(producto["nombre"])
        self.entry_nombre = QLineEdit(self)
        self.entry_nombre.setPlaceholderText("Nombre")
        self.entry_nombre.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.entry_nombre)
        self.entry_precio = QLineEdit(self)
        self.entry_precio.setPlaceholderText("Precio")
        self.entry_precio.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.entry_precio)
        self.entry_cantidad = QLineEdit(self)
        self.entry_cantidad.setPlaceholderText("Cantidad")
        self.entry_cantidad.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.entry_cantidad)
        self.entry_codigo_barra = QLineEdit(self)
        self.entry_codigo_barra.setPlaceholderText("Código de Barra")
        self.entry_codigo_barra.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.entry_codigo_barra)
        self.combo_seleccion = QComboBox(self)
        self.combo_seleccion.addItems(["Nombre", "Cantidad", "Precio"])
        self.combo_seleccion.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.combo_seleccion)
        self.guardar_btn = QPushButton("Guardar")
        self.guardar_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.guardar_btn.clicked.connect(self.insertar_actualizar_producto)
        self.layout.addWidget(self.guardar_btn)
        self.microfono_btn = QPushButton("Ingresar por Voz")
        self.microfono_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.microfono_btn.clicked.connect(self.activar_microfono)
        self.layout.addWidget(self.microfono_btn)
        self.volver_btn = QPushButton("Volver")
        self.volver_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.volver_btn.clicked.connect(self.mostrar_pantalla_opciones)
        self.layout.addWidget(self.volver_btn)

    def cargar_producto_seleccionado(self, item):
        self.entry_nombre.setText(item.text())

    def obtener_productos(self):
        db = conectar_db()
        cursor = db.cursor()
        query = "SELECT nombre, precio, cantidad FROM productos"
        cursor.execute(query)
        productos = cursor.fetchall()
        cursor.close()
        db.close()
        lista_productos = [{"nombre": prod[0], "precio": prod[1], "cantidad": prod[2]} for prod in productos]
        return lista_productos

    def obtener_producto_por_nombre(self, nombre):
        db = conectar_db()
        cursor = db.cursor()
        query = "SELECT nombre, precio, cantidad FROM productos WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        producto = cursor.fetchone()
        cursor.close()
        db.close()
        if producto:
            return {"nombre": producto[0], "precio": producto[1], "cantidad": producto[2]}
        return None

    def insertar_actualizar_producto(self):
        nombre = self.entry_nombre.text()
        precio = self.entry_precio.text()
        cantidad = self.entry_cantidad.text()
        codigo_barra = self.entry_codigo_barra.text()
        if not nombre or not precio or not cantidad:
            QMessageBox.warning(self, "Advertencia", "Todos los campos son obligatorios.")
            return
        try:
            precio = float(precio)
            cantidad = int(cantidad)
        except ValueError:
            QMessageBox.warning(self, "Advertencia", "Precio o cantidad no válidos.")
            return
        db = conectar_db()
        cursor = db.cursor()
        query = "SELECT cantidad FROM productos WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        result = cursor.fetchone()
        if result:
            nueva_cantidad = result[0] + cantidad
            update_query = "UPDATE productos SET precio = %s, cantidad = %s, codigo_barra = %s WHERE nombre = %s"
            cursor.execute(update_query, (precio, nueva_cantidad, codigo_barra, nombre))
        else:
            insert_query = "INSERT INTO productos (nombre, precio, cantidad, codigo_barra) VALUES (%s, %s, %s, %s)"
            cursor.execute(insert_query, (nombre, precio, cantidad, codigo_barra))
        db.commit()
        cursor.close()
        db.close()
        QMessageBox.information(self, "Éxito", "Producto guardado exitosamente.")
        self.entry_nombre.clear()
        self.entry_precio.clear()
        self.entry_cantidad.clear()
        self.entry_codigo_barra.clear()

    def mostrar_pantalla_restock(self):
        self.limpiar_layout()
        self.label_restock = QLabel("Productos para Restock")
        self.label_restock.setAlignment(Qt.AlignCenter)
        self.label_restock.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.label_restock)
        self.treeview_restock = QTableWidget()
        self.treeview_restock.setColumnCount(3)
        self.treeview_restock.setHorizontalHeaderLabels(["Nombre", "Cantidad", "Precio"])
        self.layout.addWidget(self.treeview_restock)
        self.cargar_productos_para_restock()
        self.volver_btn = QPushButton("Volver")
        self.volver_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.volver_btn.clicked.connect(self.mostrar_pantalla_opciones)
        self.layout.addWidget(self.volver_btn)

    def cargar_productos_para_restock(self):
        conn = conectar_db()
        cursor = conn.cursor()
        query = "SELECT nombre, cantidad, precio FROM productos WHERE cantidad = 0"
        cursor.execute(query)
        productos_restock = cursor.fetchall()
        self.treeview_restock.setRowCount(len(productos_restock))
        for row, producto in enumerate(productos_restock):
            nombre, cantidad, precio = producto
            self.treeview_restock.setItem(row, 0, QTableWidgetItem(nombre))
            self.treeview_restock.setItem(row, 1, QTableWidgetItem(str(cantidad)))
            self.treeview_restock.setItem(row, 2, QTableWidgetItem(f"${precio:.2f}"))
        cursor.close()
        conn.close()

    def mostrar_pantalla_ventas(self):
        self.limpiar_layout()
        self.label_ventas = QLabel("Ventas del Día")
        self.label_ventas.setAlignment(Qt.AlignCenter)
        self.label_ventas.setStyleSheet("font-size: 20px;")
        self.layout.addWidget(self.label_ventas)
        self.treeview_ventas = QTableWidget()
        self.treeview_ventas.setColumnCount(4)
        self.treeview_ventas.setHorizontalHeaderLabels(["Fecha", "Producto", "Cantidad", "Total"])
        self.layout.addWidget(self.treeview_ventas)
        self.cargar_ventas_del_dia()
        self.eliminar_venta_btn = QPushButton("Eliminar Venta")
        self.eliminar_venta_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.eliminar_venta_btn.clicked.connect(self.eliminar_venta)
        self.layout.addWidget(self.eliminar_venta_btn)
        self.guardar_txt_btn = QPushButton("Guardar Ventas en TXT")
        self.guardar_txt_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.guardar_txt_btn.clicked.connect(self.guardar_ventas_txt)
        self.layout.addWidget(self.guardar_txt_btn)
        self.volver_btn = QPushButton("Volver")
        self.volver_btn.setStyleSheet("font-size: 20px; background-color: red; color: black;")
        self.volver_btn.clicked.connect(self.mostrar_pantalla_opciones)
        self.layout.addWidget(self.volver_btn)

    def eliminar_venta(self):
        selected_row = self.treeview_ventas.currentRow()
        if selected_row >= 0:
            fecha = self.treeview_ventas.item(selected_row, 0).text()
            nombre = self.treeview_ventas.item(selected_row, 1).text()
            cantidad = self.treeview_ventas.item(selected_row, 2).text()
            total = self.treeview_ventas.item(selected_row, 3).text()
            total = total.replace('$', '').replace(',', '')
            respuesta = QMessageBox.question(self, "Confirmar Eliminación", 
                                         f"¿Estás seguro de que deseas eliminar la venta de {nombre} (Cantidad: {cantidad}, Total: {total})?",
                                         QMessageBox.Yes | QMessageBox.No)
            if respuesta == QMessageBox.Yes:
                try:
                    db = conectar_db()
                    cursor = db.cursor()
                    delete_query = """
                        DELETE FROM ventas 
                        WHERE fecha = %s AND nombre = %s AND cantidad = %s AND total = %s
                        LIMIT 1
                    """
                    cursor.execute(delete_query, (fecha, nombre, cantidad, total))
                    db.commit()
                    if cursor.rowcount > 0:
                        QMessageBox.information(self, "Éxito", "Venta eliminada exitosamente.")
                    else:
                        QMessageBox.warning(self, "Error", "No se encontró la venta para eliminar.")
                    cursor.close()
                    db.close()
                    self.cargar_ventas_del_dia()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error al eliminar la venta: {str(e)}")
        else:
            QMessageBox.warning(self, "Advertencia", "Por favor, selecciona una venta para eliminar.")

    def guardar_ventas_txt(self):
        db = conectar_db()
        cursor = db.cursor()
        fecha_hoy = date.today()
        query = "SELECT fecha, nombre, cantidad, total FROM ventas WHERE fecha = %s"
        cursor.execute(query, (fecha_hoy,))
        ventas = cursor.fetchall()
        total_ventas_dia = 0
        with open(f"ventas_{fecha_hoy}.txt", "w") as file:
            for venta in ventas:
                total_venta = float(venta[3])
                total_ventas_dia += total_venta
                file.write(f"Fecha: {venta[0]}, Producto: {venta[1]}, Cantidad: {venta[2]}, Total: ${total_venta:.2f}\n")
            file.write(f"\nTotal de ventas del día: ${total_ventas_dia:.2f}\n")
        cursor.close()
        db.close()
        QMessageBox.information(self, "Éxito", f"Ventas guardadas en ventas_{fecha_hoy}.txt con un total de ${total_ventas_dia:.2f}")

    def cargar_ventas_del_dia(self):
        db = conectar_db()
        cursor = db.cursor()
        fecha_hoy = date.today()
        query = "SELECT fecha, nombre, cantidad, total FROM ventas WHERE fecha = %s"
        cursor.execute(query, (fecha_hoy,))
        ventas = cursor.fetchall()
        self.treeview_ventas.setRowCount(0)
        for venta in ventas:
            row_position = self.treeview_ventas.rowCount()
            self.treeview_ventas.insertRow(row_position)
            self.treeview_ventas.setItem(row_position, 0, QTableWidgetItem(str(venta[0])))
            self.treeview_ventas.setItem(row_position, 1, QTableWidgetItem(venta[1]))
            self.treeview_ventas.setItem(row_position, 2, QTableWidgetItem(str(venta[2])))
            self.treeview_ventas.setItem(row_position, 3, QTableWidgetItem(f"${venta[3]:.2f}"))
        cursor.close()
        db.close()

    def buscar_producto(self):
        texto_busqueda = self.entry_buscar_vender.text()
        db = conectar_db()
        cursor = db.cursor()
        # Buscar por nombre o código de barra, insensible a mayúsculas/minúsculas
        query = """
            SELECT nombre, cantidad, precio FROM productos
            WHERE nombre ILIKE %s OR codigo_barra = %s
        """
        cursor.execute(query, (f"%{texto_busqueda}%", texto_busqueda))
        productos = cursor.fetchall()
        self.treeview_vender.setRowCount(0)
        for producto in productos:
            row_position = self.treeview_vender.rowCount()
            self.treeview_vender.insertRow(row_position)
            self.treeview_vender.setItem(row_position, 0, QTableWidgetItem(producto[0]))
            self.treeview_vender.setItem(row_position, 1, QTableWidgetItem(str(producto[1])))
            self.treeview_vender.setItem(row_position, 2, QTableWidgetItem(f"${producto[2]:.2f}"))
        cursor.close()
        db.close()

    def seleccionar_producto(self, row, column):
        nombre = self.treeview_vender.item(row, 0).text()
        cantidad, ok_cantidad = QInputDialog.getInt(self, "Cantidad", f"Ingrese la cantidad para {nombre}:", 1, 1, 100)
        if ok_cantidad:
            precio = float(self.treeview_vender.item(row, 2).text().replace("$", ""))
            total = cantidad * precio
            self.venta.append((nombre, cantidad, precio, total))
            self.actualizar_lista_venta()

    def actualizar_lista_venta(self):
        self.treeview_lista_venta.setRowCount(0)
        total_venta = 0.0
        for item in self.venta:
            row_position = self.treeview_lista_venta.rowCount()
            self.treeview_lista_venta.insertRow(row_position)
            self.treeview_lista_venta.setItem(row_position, 0, QTableWidgetItem(item[0]))
            self.treeview_lista_venta.setItem(row_position, 1, QTableWidgetItem(str(item[1])))
            self.treeview_lista_venta.setItem(row_position, 2, QTableWidgetItem(f"${item[2]:.2f}"))
            self.treeview_lista_venta.setItem(row_position, 3, QTableWidgetItem(f"${item[3]:.2f}"))
            total_venta += item[3]
        self.label_total.setText(f"Total: ${total_venta:.2f}")

    def eliminar_producto_lista(self):
        selected_row = self.treeview_lista_venta.currentRow()
        if selected_row >= 0:
            self.venta.pop(selected_row)
            self.actualizar_lista_venta()

    def ingresar_precio_manual(self):
        precio_manual, ok_precio = QInputDialog.getDouble(self, "Precio Manual", "Ingrese el precio manual:", 0.0, 0.0, 100000.0, 2)
        if ok_precio:
            self.venta.append(("Precio Manual", 1, precio_manual, precio_manual))
            self.actualizar_lista_venta()
        else:
            QMessageBox.warning(self, "Advertencia", "Debe ingresar un precio válido.")

    def activar_microfono(self):
        campo_seleccionado = self.combo_seleccion.currentText()
        self.label_insertar.setText(f"Escuchando para {campo_seleccionado}...")
        self.voice_thread = VoiceRecognitionThread(campo_seleccionado)
        self.voice_thread.result_ready.connect(self.procesar_texto_reconocido)
        self.voice_thread.start()

    def procesar_texto_reconocido(self, texto):
        self.label_insertar.setText(f"Texto reconocido: {texto}")
        campo_seleccionado = self.combo_seleccion.currentText()
        if campo_seleccionado == "Nombre":
            self.entry_nombre.setText(texto)
        elif campo_seleccionado == "Cantidad":
            try:
                cantidad = int(texto)
                self.entry_cantidad.setText(str(cantidad))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Cantidad '{texto}' no es válida.")
        elif campo_seleccionado == "Precio":
            try:
                precio = correccion_precio(texto)
                self.entry_precio.setText(str(precio))
            except ValueError:
                QMessageBox.warning(self, "Error", f"Precio '{texto}' no es válido.")

    def procesar_datos(self, texto):
        try:
            partes = texto.split()
            nombre = partes[0]
            cantidad = int(partes[1])
            precio = float(partes[2])
            self.entry_nombre.setText(nombre)
            self.entry_cantidad.setText(str(cantidad))
            self.entry_precio.setText(str(precio))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al procesar los datos: {e}")

    # ... (Aquí irían el resto de los métodos: mostrar_pantalla_vender, confirmar_venta, on_metodo_pago_changed, mostrar_qr_mercado_pago, procesar_venta_efectivo, confirmar_pago_mercado_pago, activar_microfono, procesar_texto_reconocido, procesar_datos, insertar_actualizar_producto, mostrar_pantalla_restock, cargar_productos_para_restock, mostrar_pantalla_ventas, eliminar_venta, guardar_ventas_txt, mostrar_pantalla_insertar, cargar_producto_seleccionado, obtener_productos, obtener_producto_por_nombre, cargar_ventas_del_dia, buscar_producto, seleccionar_producto, actualizar_lista_venta, eliminar_producto_lista, ingresar_precio_manual, etc.)
    # Si necesitas que los agregue todos completos, avísame y los pego aquí uno por uno.

    # --- Métodos de la clase MainWindow ---
    # (Aquí van todos los métodos de la clase MainWindow que estaban en main.py, adaptados a rutas relativas y usando los imports correctos)
    # Por razones de espacio, si necesitas que pegue todos los métodos aquí, avísame y los agrego completos.

    # ... el resto de la clase MainWindow, igual que en main.py, pero usando rutas relativas para imágenes ... 