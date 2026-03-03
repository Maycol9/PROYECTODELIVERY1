import os
import json
import csv
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- 1. CONFIGURACIÓN DE INFRAESTRUCTURA (Punto 2.1 y 2.3) ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configuración profesional de SQLAlchemy (ORM)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'puyo_delivery.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Creación de ruta de almacenamiento local: inventario/data/
DATA_DIR = os.path.join(BASE_DIR, 'inventario', 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 2. MODELO DE DATOS CON ENCAPSULAMIENTO (Punto 2.4) ---
class Producto(db.Model):
    __tablename__ = 'inventario_puyo'
    
    id_prod = db.Column('id', db.Integer, primary_key=True)
    _nombre = db.Column('nombre', db.String(100), nullable=False) # Atributo privado
    cantidad = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    restaurante = db.Column(db.String(100), nullable=False)

    # Getters para acceso seguro (Encapsulamiento POO)
    def get_id(self): 
        return self.id_prod
        
    def get_nombre(self): 
        return self._nombre

# Inicialización de la base de datos
with app.app_context():
    db.create_all()

# --- 3. LÓGICA DE PERSISTENCIA TRIPLE (Punto 2.2) ---

def guardar_en_archivos(p_dict):
    """Sincroniza datos en TXT, JSON y CSV simultáneamente."""
    
    # A. Respaldo en Texto Plano (TXT)
    with open(os.path.join(DATA_DIR, 'datos.txt'), 'a') as f:
        f.write(f"ID: {p_dict['id']} | {p_dict['nombre']} | {p_dict['restaurante']}\n")

    # B. Respaldo Estructurado (JSON)
    json_path = os.path.join(DATA_DIR, 'datos.json')
    json_list = []
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            try: json_list = json.load(f)
            except: json_list = []
    json_list.append(p_dict)
    with open(json_path, 'w') as f:
        json.dump(json_list, f, indent=4)

    # C. Respaldo Tabular (CSV)
    csv_path = os.path.join(DATA_DIR, 'datos.csv')
    is_new = not os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=p_dict.keys())
        if is_new: writer.writeheader()
        writer.writerow(p_dict)

# --- 4. INTERFAZ PROFESIONAL (HTML/CSS) ---

ESTILOS_PRO = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    :root { --puyo-orange: #FF5A00; --puyo-black: #1A1A1A; --puyo-bg: #F8F9FA; }
    body { font-family: 'Inter', sans-serif; background: var(--puyo-bg); margin: 0; color: var(--puyo-black); }
    .nav { background: var(--puyo-black); padding: 1.2rem 10%; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
    .logo { color: white; font-size: 1.5rem; font-weight: 800; text-decoration: none; }
    .logo span { color: var(--puyo-orange); }
    .card { max-width: 1000px; margin: 3rem auto; background: white; padding: 2.5rem; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); }
    .form-grid { background: #f1f3f5; padding: 25px; border-radius: 15px; margin-bottom: 2.5rem; display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px; }
    input { border: 1px solid #ddd; padding: 12px; border-radius: 8px; outline: none; transition: 0.3s; }
    input:focus { border-color: var(--puyo-orange); box-shadow: 0 0 0 3px rgba(255,90,0,0.1); }
    .btn-add { background: var(--puyo-orange); color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; }
    .btn-add:hover { background: #E65100; transform: translateY(-2px); }
    table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
    th { text-align: left; padding: 15px; color: #888; font-size: 0.75rem; text-transform: uppercase; }
    td { padding: 18px; border-bottom: 1px solid #eee; }
    .id-tag { background: #eee; padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 0.8rem; }
    .btn-data { background: #333; color: white; text-decoration: none; padding: 10px 15px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; }
</style>
"""

@app.route('/')
def home():
    productos = Producto.query.all()
    html = ESTILOS_PRO + """
    <nav class="nav">
        <a href="/" class="logo">PUYO<span>DELIVERY</span></a>
        <a href="/datos" class="btn-data">🔍 PERSISTENCIA LOCAL</a>
    </nav>
    <div class="card">
        <h2 style="margin-top:0;">Gestión de Inventario (ORM + Archivos)</h2>
        <form class="form-grid" action="/add" method="post">
            <input name="id" placeholder="ID" type="number" required>
            <input name="nombre" placeholder="Producto" required>
            <input name="cant" placeholder="Stock" type="number" required>
            <input name="precio" placeholder="Precio" type="number" step="0.01" required>
            <input name="rest" placeholder="Restaurante" required>
            <button type="submit" class="btn-add">GUARDAR TODO</button>
        </form>
        <table>
            <tr><th>ID</th><th>Nombre</th><th>Stock</th><th>Precio</th><th>Restaurante</th><th>Acción</th></tr>
    """
    for p in productos:
        html += f"""
            <tr>
                <td><span class="id-tag">#{p.get_id()}</span></td>
                <td><strong>{p.get_nombre()}</strong></td>
                <td>{p.cantidad} unds.</td>
                <td><b>${p.precio:.2f}</b></td>
                <td>{p.restaurante}</td>
                <td><a href="/del/{p.id_prod}" style="color:#d32f2f; text-decoration:none; font-weight:bold;">Eliminar</a></td>
            </tr>
        """
    html += "</table></div>"
    return render_template_string(html)

@app.route('/add', methods=['POST'])
def add():
    try:
        p_id = int(request.form['id'])
        p_nom = request.form['nombre']
        p_can = int(request.form['cant'])
        p_pre = float(request.form['precio'])
        p_res = request.form['rest']

        # 1. Persistencia ORM
        nuevo = Producto(id_prod=p_id, _nombre=p_nom, cantidad=p_can, precio=p_pre, restaurante=p_res)
        db.session.add(nuevo)
        db.session.commit()

        # 2. Persistencia en Archivos
        p_dict = {"id": p_id, "nombre": p_nom, "cantidad": p_can, "precio": p_pre, "restaurante": p_res}
        guardar_en_archivos(p_dict)
    except Exception:
        db.session.rollback()
    return redirect(url_for('home'))

@app.route('/del/<int:id>')
def delete(id):
    p = Producto.query.get(id)
    if p:
        db.session.delete(p)
        db.session.commit()
    return redirect(url_for('home'))

# RUTA PARA VISUALIZAR LOS ARCHIVOS (REQUISITO 2.2)
@app.route('/datos')
def show_files():
    # Lectura de archivos para visualización
    data = {"txt": "Vacío", "json": [], "csv": []}
    if os.path.exists(os.path.join(DATA_DIR, 'datos.txt')):
        with open(os.path.join(DATA_DIR, 'datos.txt'), 'r') as f: data['txt'] = f.read()
    if os.path.exists(os.path.join(DATA_DIR, 'datos.json')):
        with open(os.path.join(DATA_DIR, 'datos.json'), 'r') as f:
            try: data['json'] = json.load(f)
            except: pass
    if os.path.exists(os.path.join(DATA_DIR, 'datos.csv')):
        with open(os.path.join(DATA_DIR, 'datos.csv'), 'r') as f:
            data['csv'] = list(csv.DictReader(f))

    return render_template_string("""
    <body style="background:#121212; color:white; font-family:Inter; padding:50px;">
        <a href="/" style="color:#FF5A00; text-decoration:none; font-weight:bold;">← VOLVER</a>
        <h1>Lectura de Persistencia Local (Semana 12)</h1>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px;">
            <div style="background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid orange;">
                <h3>📄 TXT LOGS</h3><pre>{{ txt }}</pre>
            </div>
            <div style="background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid green;">
                <h3>📦 JSON DATA</h3><pre>{{ json }}</pre>
            </div>
        </div>
        <div style="background:#1e1e1e; padding:20px; border-radius:10px; border-left:5px solid blue; margin-top:20px;">
            <h3>📊 CSV REPORT</h3><pre>{{ csv }}</pre>
        </div>
    </body>
    """, txt=data['txt'], json=json.dumps(data['json'], indent=2), csv=data['csv'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)), debug=False)