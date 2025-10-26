from typing import List, Dict, Tuple, Optional
from datetime import date
from db import conectar_db


def search_products(query: str) -> List[Dict]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        if query:
            cur.execute(
                """
                SELECT nombre, cantidad, precio FROM productos
                WHERE nombre ILIKE %s OR codigo_barra = %s
                ORDER BY nombre ASC
                """,
                (f"%{query}%", query),
            )
        else:
            cur.execute(
                "SELECT nombre, cantidad, precio FROM productos ORDER BY nombre ASC LIMIT 100"
            )
        rows = cur.fetchall()
        return [
            {"nombre": r[0], "cantidad": int(r[1]), "precio": float(r[2])}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def restock_products() -> List[Dict]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT nombre, cantidad, precio FROM productos WHERE cantidad = 0 ORDER BY nombre ASC"
        )
        rows = cur.fetchall()
        return [
            {"nombre": r[0], "cantidad": int(r[1]), "precio": float(r[2])}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def sales_of_day(day: date) -> List[Dict]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT fecha, nombre, cantidad, total FROM ventas WHERE fecha = %s ORDER BY nombre ASC",
            (day,),
        )
        rows = cur.fetchall()
        return [
            {"fecha": str(r[0]), "nombre": r[1], "cantidad": int(r[2]), "total": float(r[3])}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def checkout_items(items: List[Dict]) -> Tuple[bool, str]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        for item in items:
            nombre = item.get("nombre")
            cantidad = int(item.get("cantidad", 1))
            precio = float(item.get("precio", 0))
            total = cantidad * precio
            cur.execute(
                "INSERT INTO ventas (fecha, nombre, cantidad, total) VALUES (%s, %s, %s, %s)",
                (date.today(), nombre, cantidad, total),
            )
            cur.execute(
                "UPDATE productos SET cantidad = cantidad - %s WHERE nombre = %s",
                (cantidad, nombre),
            )
        conn.commit()
        return True, ""
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        cur.close()
        conn.close()


# --- Funciones adicionales para gestión completa ---

def list_products() -> List[Dict]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT nombre, precio, cantidad, COALESCE(codigo_barra,'') FROM productos ORDER BY nombre ASC")
        rows = cur.fetchall()
        return [
            {"nombre": r[0], "precio": float(r[1]), "cantidad": int(r[2]), "codigo_barra": r[3]}
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def get_product_by_name(nombre: str) -> Optional[Dict]:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT nombre, precio, cantidad, COALESCE(codigo_barra,'') FROM productos WHERE nombre = %s", (nombre,))
        r = cur.fetchone()
        if r:
            return {"nombre": r[0], "precio": float(r[1]), "cantidad": int(r[2]), "codigo_barra": r[3]}
        return None
    finally:
        cur.close()
        conn.close()


def upsert_product(nombre: str, precio: float, cantidad: int, codigo_barra: str) -> None:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT cantidad FROM productos WHERE nombre = %s", (nombre,))
        row = cur.fetchone()
        if row:
            nueva_cantidad = int(row[0]) + int(cantidad)
            cur.execute(
                "UPDATE productos SET precio=%s, cantidad=%s, codigo_barra=%s WHERE nombre=%s",
                (precio, nueva_cantidad, codigo_barra, nombre),
            )
        else:
            cur.execute(
                "INSERT INTO productos (nombre, precio, cantidad, codigo_barra) VALUES (%s,%s,%s,%s)",
                (nombre, precio, cantidad, codigo_barra),
            )
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_one_sale(fecha: str, nombre: str, cantidad: str, total: str) -> bool:
    """Elimina una sola fila que coincida usando ctid para simular LIMIT 1 en DELETE."""
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            DELETE FROM ventas
            WHERE ctid IN (
                SELECT ctid FROM ventas
                WHERE fecha = %s AND nombre = %s AND cantidad = %s AND total = %s
                LIMIT 1
            )
            """,
            (fecha, nombre, cantidad, total),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def sales_txt_for_day(day: date) -> str:
    conn = conectar_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT fecha, nombre, cantidad, total FROM ventas WHERE fecha = %s", (day,))
        ventas = cur.fetchall()
        total_ventas_dia = 0.0
        lines: List[str] = []
        for v in ventas:
            t = float(v[3])
            total_ventas_dia += t
            lines.append(f"Fecha: {v[0]}, Producto: {v[1]}, Cantidad: {v[2]}, Total: ${t:.2f}")
        lines.append("")
        lines.append(f"Total de ventas del día: ${total_ventas_dia:.2f}")
        return "\n".join(lines)
    finally:
        cur.close()
        conn.close()


