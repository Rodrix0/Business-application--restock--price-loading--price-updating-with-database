from flask import Flask, render_template, request, jsonify
from datetime import date
import os, sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from services.store import (
    search_products, restock_products, sales_of_day, checkout_items,
    list_products, get_product_by_name, upsert_product, delete_one_sale, sales_txt_for_day
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/sell")
    def sell_page():
        return render_template("sell.html")

    @app.route("/restock")
    def restock_page():
        return render_template("restock.html", productos=restock_products())

    @app.route("/sales")
    def sales_page():
        hoy = date.today()
        ventas = sales_of_day(hoy)
        total_dia = sum(v["total"] for v in ventas)
        return render_template("sales.html", ventas=ventas, total_dia=total_dia, fecha=hoy)

    @app.route("/manage")
    def manage_page():
        return render_template("manage.html", productos=list_products())

    @app.get("/api/products")
    def api_products():
        q = request.args.get("q", "").strip()
        return jsonify({"items": search_products(q)})

    @app.post("/api/checkout")
    def api_checkout():
        payload = request.get_json(silent=True) or {}
        ok, err = checkout_items(payload.get("items", []))
        if not ok:
            return jsonify({"ok": False, "error": err}), 500
        return jsonify({"ok": True})

    @app.get("/api/product")
    def api_get_product():
        nombre = request.args.get("nombre", "")
        prod = get_product_by_name(nombre) if nombre else None
        return jsonify({"item": prod})

    @app.post("/api/product")
    def api_upsert_product():
        data = request.get_json(silent=True) or {}
        try:
            upsert_product(
                data.get("nombre",""), float(data.get("precio",0)), int(data.get("cantidad",0)), data.get("codigo_barra","")
            )
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 400

    @app.post("/api/sales/delete")
    def api_delete_sale():
        data = request.get_json(silent=True) or {}
        ok = delete_one_sale(data.get("fecha",""), data.get("nombre",""), data.get("cantidad",""), data.get("total",""))
        return jsonify({"ok": ok})

    @app.get("/api/sales/txt")
    def api_sales_txt():
        today = date.today()
        content = sales_txt_for_day(today)
        return content, 200, {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': f'attachment; filename="ventas_{today}.txt"'
        }

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


