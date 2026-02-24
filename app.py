import sqlite3
import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- 1. CLASE PRODUCTO (Requisito: POO y Encapsulamiento) ---
class Producto:
    def __init__(self, id_prod, nombre, cantidad, precio, restaurante):
        # Atributos privados (__) para cumplir con el encapsulamiento
        self.__id = id_prod  
        self.__nombre = nombre 
        self.cantidad = cantidad
        self.precio = precio
        self.restaurante = restaurante

    # Getters para acceder a datos privados de forma segura
    def get_id(self): 
        return self.__id
        
    def get_nombre(self): 
        return self.__nombre

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
                # Creamos el objeto Producto usando los datos de la DB
                p = Producto(f[0], f[1], f[2], f[3], f[4])
                # Guardamos en el diccionario usando el ID como llave
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

# --- 3. RUTAS FLASK (Interfaz Web para el profesor) ---

@app.route('/')
def home():
    inv = Inventario()
    html = """
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f8f9fa; color: #333; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 900px; margin: auto; }
        h1 { color: #e44d26; text-align: center; }
        .form-group { background: #fff5f2; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ffe0d6; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #eee; text-align: left; }
        th { background: #e44d26; color: white; }
        .btn-del { color: #dc3545; text-decoration: none; font-weight: bold; }
        input { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        button:hover { background: #218838; }
    </style>
    <div class="card">
        <h1>🛵 Puyo Delivery - Gestión de Inventario</h1>
        <p style="text-align:center;">Persistencia: <b>SQLite</b> | Colección: <b>Diccionario</b></p>
        
        <div class="form-group">
            <form action="/add" method="post">
                <input name="id" placeholder="ID (Num)" type="number" required style="width: 80px;">
                <input name="nombre" placeholder="Nombre Producto" required>
                <input name="cant" placeholder="Stock" type="number" required style="width: 80px;">
                <input name="precio" placeholder="Precio" type="number" step="0.01" required style="width: 80px;">
                <input name="rest" placeholder="Restaurante" required>
                <button type="submit">Añadir Producto</button>
            </form>
        </div>

        <table>
            <tr><th>ID</th><th>Nombre</th><th>Stock</th><th>Precio</th><th>Restaurante</th><th>Acción</th></tr>
    """
    for p in inv.productos_coleccion.values():
        html += f"""
            <tr>
                <td>{p.get_id()}</td>
                <td>{p.get_nombre()}</td>
                <td>{p.cantidad} unidades</td>
                <td>${p.precio:.2f}</td>
                <td>{p.restaurante}</td>
                <td><a href="/del/{p.get_id()}" class="btn-del" onclick="return confirm('¿Eliminar?')">Eliminar</a></td>
            </tr>
        """
    html += "</table></div>"
    return render_template_string(html)

@app.route('/add', methods=['POST'])
def add():
    inv = Inventario()
    try:
        nuevo_p = Producto(
            int(request.form['id']), 
            request.form['nombre'], 
            int(request.form['cant']), 
            float(request.form['precio']), 
            request.form['rest']
        )
        inv.añadir(nuevo_p)
    except: pass
    return "<script>window.location='/';</script>"

@app.route('/del/<int:id_p>')
def delete(id_p):
    inv = Inventario()
    inv.eliminar(id_p)
    return "<script>window.location='/';</script>"

# --- 4. CONFIGURACIÓN DE PUERTO PARA RENDER ---
if __name__ == '__main__':
    # Usamos el puerto 10000 que configuramos en el panel de Render
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)