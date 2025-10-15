from flask import Flask, render_template, request
import os

app = Flask(__name__)

def extraer_datos(nombre, texto):
    lineas = [line.strip() for line in texto.strip().splitlines() if line.strip()]
    
    # Archivos tipo tabla (.txt con ;)
    if nombre.endswith('.txt') and ';' in lineas[1]:
        datos = lineas[1].split(';')
        try:
            temperatura = float(datos[4].strip())
            presion = float(datos[8].strip())
            direccion = datos[9].strip()
            velocidad = float(datos[10].strip())
            humedad = float(datos[6].strip())
            bateria = float(datos[17].strip())
        except (ValueError, IndexError):
            temperatura = presion = velocidad = humedad = bateria = None
            direccion = "?"
        return temperatura, presion, velocidad, direccion, bateria, humedad

    # Archivos tipo TOA5 (línea con fecha y suficientes columnas)
    for linea in lineas:
        if ("2025-10-15" in linea or "2025-10-14" in linea) and linea.count(',') >= 25:
            campos = linea.split(',')
            try:
                temperatura = float(campos[16].strip())
                presion = float(campos[23].strip())
                direccion = campos[12].strip()
                velocidad = float(campos[11].strip())
                humedad = float(campos[21].strip())
                bateria = float(campos[2].strip())
            except (ValueError, IndexError):
                temperatura = presion = velocidad = humedad = bateria = None
                direccion = "?"
            return temperatura, presion, velocidad, direccion, bateria, humedad

    return None, None, None, "?", None, None

def generar_alertas(temperatura, presion, velocidad, direccion, bateria, humedad):
    alertas = []

    if bateria is None or bateria < 12.5:
        alertas.append("🔋 Batería baja – Sin 220V")

    if temperatura is None or presion is None or velocidad is None or direccion == "?":
        alertas.append("❌ Sensor no disponible")

    if temperatura is not None and temperatura < -5:
        alertas.append("🌡️ Temperatura extremadamente baja")

    if humedad is not None and humedad > 100:
        alertas.append("💧 Humedad fuera de rango")

    return alertas

def evaluar_estacion(nombre, temperatura, presion, velocidad, direccion, bateria, humedad):
    if bateria is None:
        estado = "⚠️ Voltaje no encontrado"
    elif bateria < 12.5:
        estado = "🔴 Sin 220V"
    else:
        estado = "🟢 Con 220V"

    alertas = generar_alertas(temperatura, presion, velocidad, direccion, bateria, humedad)

    return {
        "nombre": nombre,
        "temperatura": temperatura,
        "presion": presion,
        "velocidad": velocidad,
        "direccion": direccion,
        "bateria": bateria,
        "humedad": humedad,
        "estado": estado,
        "alertas": alertas
    }

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    archivos = request.files.getlist('archivos')
    resultados = []
    nombres_subidos = [archivo.filename.lower() for archivo in archivos]
    falta_la_carolina = not any("carolina" in nombre for nombre in nombres_subidos)

    for archivo in archivos:
        nombre = archivo.filename
        contenido = archivo.read().decode('utf-8')
        temperatura, presion, velocidad, direccion, bateria, humedad = extraer_datos(nombre, contenido)
        resultado = evaluar_estacion(nombre, temperatura, presion, velocidad, direccion, bateria, humedad)
        resultados.append(resultado)

    return render_template('dashboard.html', resultados=resultados, falta_la_carolina=falta_la_carolina)

if __name__ == '__main__':
    app.run(debug=True)
