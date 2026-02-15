from flask import Flask

app = Flask(__name__)

# Ruta principal
@app.route('/')
def inicio():
    return "Bienvenido a PUYO DELIVERY - Pedidos rápidos en la ciudad de Puyo"

# Ruta dinámica para clientes/pedidos
@app.route('/pedido/<cliente>')
def pedido(cliente):
    return f"Cliente: {cliente}. Tu pedido está en proceso de confirmación y asignación de repartidor."

# Ruta dinámica para categoría/tipo de servicio
@app.route('/categoria/<nombre>')
def categoria(nombre):
    return f"Categoría solicitada: {nombre}. Disponibilidad sujeta al horario del local y repartidores."

# Ruta dinámica para ver estado por ID
@app.route('/estado/<int:id_pedido>')
def estado(id_pedido):
    return f"Pedido #{id_pedido}: En preparación. Te notificaremos cuando salga a reparto."

if __name__ == "__main__":
    app.run(debug=True)

