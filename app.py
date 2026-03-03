import os
import json
import csv
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURACIÓN DE PERSISTENCIA (Semana 12) ---
basedir = os.path.abspath(os.path.dirname(__file__))
# Configuración de SQLite usando SQLAlchemy (ORM)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'puyo_delivery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Carpeta para archivos planos según estructura solicitada
DATA_DIR = os.path.join(basedir, 'inventario', 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 1. CLASE PRODUCTO (Requisito: POO, Encapsulamiento y ORM) ---
class Producto(db.Model):
    __tablename__ = 'productos'
    # Atributos que mapean a la base de datos
    id = db.Column(db.Integer, primary_key=True)
    _nombre = db.Column('nombre', db.String(100), nullable=False) # Encapsulamiento en BD
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    restaurante = db.Column(db.String(100), nullable=False)

    # Getters para cumplir con el requisito de encapsulamiento del profesor
    def get_id(self): 
        return self.id
        
    def get_nombre(self): 
        return self._nombre

# Crear la base de datos automáticamente
with app.app_context():
    db.create_all()

# --- 2. LÓGICA DE PERSISTENCIA EN ARCHIVOS (Punto 2.2 de la tarea) ---
def guardar_en_archivos(p_dict):
    # A. Guardar en TXT (usando open() en modo append)
    with open(os.path.join(DATA_DIR, 'datos.txt'), 'a') as f:
        f.write(f"ID: {p_dict['id']} | Producto: {p_dict['nombre']} | Restaurante: {p_dict['restaurante']}\n")

    # B. Guardar en JSON (librería json)
    json_path = os.path.join(DATA_DIR, 'datos.json')
    datos_json = []
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try: datos_json = json.load(f)
            except: datos_json = []
    datos_json.append(p_dict)
    with open(json_path, 'w') as f:
        json.dump(datos_json, f, indent=4)

    # C. Guardar en CSV (librería csv)
    csv_path = os.path.join(DATA_DIR, 'datos.csv')
    es_nuevo = not os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=p_dict.keys())
        if es_nuevo: writer.writeheader()
        writer.writerow(p_dict)

def leer_archivos_planos():
    """Lee los archivos para mostrarlos en la nueva ruta de datos."""
    resultado = {"txt": "", "json": [], "csv": []}
    if os.path.exists(os.path.join(DATA_DIR, 'datos.txt')):
        with open(os.path.join(DATA_DIR, 'datos.txt'), 'r') as f: resultado["txt"] = f.read()
    if os.path.exists(os.path.join(DATA_DIR, 'datos.json')):
        with open(os.path.join(DATA_DIR, 'datos.json'), 'r') as f: 
            try: resultado["json"] = json.load(f)
            except: pass
    if os.path.exists(os.path.join(DATA_DIR, 'datos.csv')):
        with open(os.path.join(DATA_DIR, 'datos.csv'), 'r') as f:
            resultado["csv"] = list(csv.DictReader(f))
    return resultado

# --- 3. RUTAS FLASK ---

@app.route('/')
def home():
    # Consulta usando SQLAlchemy (ORM)
    productos = Producto.query.all()
    
    html = """
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f8f9fa; color: #333; }
        .card { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); max-width: 950px; margin: auto; }
        h1 { color: #e44d26; text-align: center; }
        .form-group { background: #fff5f2; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #ffe0d6; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border: 1px solid #eee; text-align: left; }
        th { background: #e44d26; color: white; }
        .btn-del { color: #dc3545; text-decoration: none; font-weight: bold; }
        input { padding: 10px; margin: 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .nav-btn { background: #007bff; display: inline-block; padding: 10px; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 10px; }
    </style>
    <div class="card">
        <h1>🛵 Puyo Delivery - Sistema Integrado</h1>
        <p style="text-align:center;">Persistencia: <b>SQLAlchemy (ORM) + Archivos (JSON, CSV, TXT)</b></p>
        
        <div style="text-align: center;">
            <a href="/datos" class="nav-btn">🔍 Ver Persistencia en Archivos</a>
        </div>

        <div class="form-group">
            <form action="/add" method="post">
                <input name="id" placeholder="ID" type="number" required style="width: 60px;">
                <input name="nombre" placeholder="Producto" required>
                <input name="cant" placeholder="Stock" type="number" required style="width: 70px;">
                <input name="precio" placeholder="Precio" type="number" step="0.01" required style="width: 80px;">
                <input name="rest" placeholder="Restaurante" required>
                <button type="submit">Guardar en Todo el Sistema</button>
            </form>
        </div>

        <table>
            <tr><th>ID</th><th>Nombre</th><th>Stock</th><th>Precio</th><th>Restaurante</th><th>Acción</th></tr>
    """
    for p in productos:
        html += f"""
            <tr>
                <td>{p.get_id()}</td>
                <td>{p.get_nombre()}</td>
                <td>{p.cantidad} unidades</td>
                <td>${p.precio:.2f}</td>
                <td>{p.restaurante}</td>
                <td><a href="/del/{p.id}" class="btn-del" onclick="return confirm('¿Eliminar?')">Eliminar</a></td>
            </tr>
        """
    html += "</table></div>"
    return render_template_string(html)

@app.route('/add', methods=['POST'])
def add():
    try:
        # 1. Datos del formulario
        p_id = int(request.form['id'])
        nombre = request.form['nombre']
        cantidad = int(request.form['cant'])
        precio = float(request.form['precio'])
        restaurante = request.form['rest']

        # 2. Persistencia en DB con SQLAlchemy (Punto 2.3)
        nuevo_p = Producto(id=p_id, _nombre=nombre, cantidad=cantidad, precio=precio, restaurante=restaurante)
        db.session.add(nuevo_p)
        db.session.commit()

        # 3. Persistencia en archivos (Punto 2.2)
        dict_datos = {"id": p_id, "nombre": nombre, "cantidad": cantidad, "precio": precio, "restaurante": restaurante}
        guardar_en_archivos(dict_datos)
        
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
        
    return redirect(url_for('home'))

@app.route('/del/<int:id_p>')
def delete(id_p):
    prod = Producto.query.get(id_p)
    if prod:
        db.session.delete(prod)
        db.session.commit()
    return redirect(url_for('home'))

# RUTA NUEVA PARA SEMANA 12: Muestra la persistencia en archivos
@app.route('/datos')
def datos():
    data = leer_archivos_planos()
    html = f"""
    <body style="font-family: sans-serif; margin: 40px; background: #f0f2f5;">
        <a href="/" style="text-decoration: none; color: #007bff; font-weight: bold;">← Volver al Sistema</a>
        <h1>Lectura de Persistencia Local (Semana 12)</h1>
        
        <div style="background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #ffc107;">
            <h3>📄 Archivo TXT (Lectura plana)</h3>
            <pre>{data['txt']}</pre>
        </div>

        <div style="background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #28a745;">
            <h3>📦 Archivo JSON (Diccionario serializado)</h3>
            <pre>{json.dumps(data['json'], indent=2)}</pre>
        </div>

        <div style="background: white; padding: 20px; margin-bottom: 20px; border-radius: 10px; border-left: 5px solid #17a2b8;">
            <h3>📊 Archivo CSV (Registros estructurados)</h3>
            <pre>{data['csv']}</pre>
        </div>
    </body>
    """
    return render_template_string(html)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)