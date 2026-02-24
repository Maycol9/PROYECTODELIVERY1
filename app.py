import sqlite3
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- 1. CLASE PRODUCTO (POO + Encapsulamiento) ---
class Producto:
    def __init__(self, id_prod, nombre, cantidad, precio, restaurante):
        self.__id = id_prod  
        self.__nombre = nombre 
        self.cantidad = cantidad
        self.precio = precio
        self.restaurante = restaurante

    def get_id(self): return self.__id
    def get_nombre(self): return self.__nombre

# --- 2. CLASE INVENTARIO (Diccionarios + SQLite) ---
class Inventario:
    def __init__(self):
        self.db_path = "puyo_delivery.db"
        self.productos_coleccion = {} # Diccionario O(1)
        self._conectar_db()
        self._sincronizar()

    def _conectar_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS productos (id INTEGER PRIMARY KEY, nombre TEXT, cantidad INTEGER, precio REAL, restaurante TEXT)")

    def _sincronizar(self):
        self.productos_coleccion.clear()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos")
            for f in cursor.fetchall():
                p = Producto(f[0], f[1], f[2], f[3], f[4])
                self.productos_coleccion[p.get_id()] = p

    def añadir(self, p):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO productos VALUES (?,?,?,?,?)", (p.get_id(), p.get_nombre(), p.cantidad, p.precio, p.restaurante))
        self.productos_coleccion[p.get_id()] = p

# --- 3. RUTA PRINCIPAL (Interfaz Web) ---
@app.route('/')
def home():
    inv = Inventario()
    # Diseño minimalista y funcional
    html = """
    <body style="font-family: sans-serif; padding: 50px; background: #f4f4f9;">
        <div style="background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); max-width: 600px; margin: auto;">
            <h1 style="color: #e44d26;">🛵 Puyo Delivery - Inventario</h1>
            <form action="/add" method="post">
                <input name="id" placeholder="ID" type="number" required style="width: 50px; padding: 5px;">
                <input name="nombre" placeholder="Nombre" required style="padding: 5px;">
                <input name="cant" placeholder="Stock" type="number" required style="width: 60px; padding: 5px;">
                <input name="precio" placeholder="Precio" type="number" step="0.01" required style="width: 70px; padding: 5px;">
                <button type="submit" style="background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">Añadir</button>
            </form>
            <table border="1" style="width: 100%; margin-top: 20px; border-collapse: collapse;">
                <tr style="background: #e44d26; color: white;"><th>ID</th><th>Nombre</th><th>Stock</th><th>Precio</th></tr>
    """
    for p in inv.productos_coleccion.values():
        html += f"<tr><td>{p.get_id()}</td><td>{p.get_nombre()}</td><td>{p.cantidad}</td><td>${p.precio:.2f}</td></tr>"
    html += "</table></div></body>"
    return render_template_string(html)

@app.route('/add', methods=['POST'])
def add():
    inv = Inventario()
    try:
        p = Producto(int(request.form['id']), request.form['nombre'], int(request.form['cant']), float(request.form['precio']), "Local Puyo")
        inv.añadir(p)
    except: pass
    return "<script>window.location='/';</script>"

# --- 4. CONFIGURACIÓN CRUCIAL PARA RENDER ---
if __name__ == '__main__':
    # Render usa la variable de entorno PORT, si no existe usa 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)