import sqlite3
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- 1. CLASE PRODUCTO (Requisito: POO y Encapsulamiento) ---
class Producto:
    def __init__(self, id_prod, nombre, cantidad, precio, restaurante):
        self.__id = id_prod  # Atributo privado
        self.__nombre = nombre # Atributo privado
        self.cantidad = cantidad
        self.precio = precio
        self.restaurante = restaurante

    # Getters para acceder a datos protegidos
    def get_id(self): return self.__id
    def get_nombre(self): return self.__nombre

# --- 2. CLASE INVENTARIO (Requisito: Colecciones y SQLite) ---
class Inventario:
    def __init__(self):
        self.db_path = "puyo_delivery.db"
        self.productos_coleccion = {} # Diccionario para búsqueda eficiente O(1)
        self._conectar_db()
        self._sincronizar()

    def _conectar_db(self):
        """Crea la tabla en SQLite si no existe."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    cantidad INTEGER,
                    precio REAL,
                    restaurante TEXT
                )
            """)

    def _sincronizar(self):
        """Carga datos de SQLite al Diccionario en memoria."""
        self.productos_coleccion.clear()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM productos")
            for f in cursor.fetchall():
                p = Producto(f[0], f[1], f[2], f[3], f[4])
                self.productos_coleccion[p.get_id()] = p

    def añadir(self, p):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO productos VALUES (?,?,?,?,?)",
                         (p.get_id(), p.get_nombre(), p.cantidad, p.precio, p.restaurante))
        self.productos_coleccion[p.get_id()] = p

    def eliminar(self, id_prod):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM productos WHERE id = ?", (id_prod,))
        if id_prod in self.productos_coleccion:
            del self.productos_coleccion[id_prod]

# --- 3. RUTAS FLASK (Interfaz para Render) ---

@app.route('/')
def home():
    inv = Inventario()
    html = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #e9ecef; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); max-width: 900px; margin: auto; }
        h1 { color: #d9534f; border-bottom: 2px solid #d9534f; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; }
        th, td { padding: 12px; border: 1px solid #dee2e6; text-align: left; }
        th { background-color: #f8f9fa; }
        .btn-del { color: #d9534f; text-decoration: none; font-weight: bold; }
        input { padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-right: 5px; }
        button { padding: 10px 20px; background: #5cb85c; color: white; border: none; border-radius: 4px; cursor: pointer; }
    </style>
    <div class="card">
        <h1>🛵 Puyo Delivery - Inventario Local</h1>
        <h3>Registrar nuevo producto</h3>
        <form action="/add" method="post">
            <input name="id" placeholder="ID" type="number" required style="width: 60px;">
            <input name="nombre" placeholder="Nombre del plato" required>
            <input name="cant" placeholder="Stock" type="number" required style="width: 80px;">
            <input name="precio" placeholder="Precio" type="number" step="0.01" required style="width: 80px;">
            <input name="rest" placeholder="Restaurante" required>
            <button type="submit">Agregar</button>
        </form>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Stock</th><th>Precio</th><th>Local</th><th>Acción</th></tr>
    """
    for p in inv.productos_coleccion.values():
        html += f"""
            <tr>
                <td>{p.get_id()}</td>
                <td>{p.get_nombre()}</td>
                <td>{p.cantidad}</td>
                <td>${p.precio:.2f}</td>
                <td>{p.restaurante}</td>
                <td><a href="/del/{p.get_id()}" class="btn-del">❌ Eliminar</a></td>
            </tr>
        """
    html += "</table></div>"
    return render_template_string(html)

@app.route('/add', methods=['POST'])
def add():
    inv = Inventario()
    try:
        p = Producto(int(request.form['id']), request.form['nombre'],
                     int(request.form['cant']), float(request.form['precio']), request.form['rest'])
        inv.añadir(p)
    except: pass
    return "<script>window.location='/';</script>"

@app.route('/del/<int:id_p>')
def delete(id_p):
    inv = Inventario()
    inv.eliminar(id_p)
    return "<script>window.location='/';</script>"

if __name__ == '__main__':
    # ESTO ES LO QUE HACE QUE FUNCIONE EN RENDER
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
