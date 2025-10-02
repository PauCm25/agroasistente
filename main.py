from openai import OpenAI
from flask import Flask, request, jsonify, render_template
import os

# 🔐 Clave API desde variable de entorno
client = OpenAI(api_key=os.getenv("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"))

# 🧠 Instrucciones para AgroAsistente
system_prompt = (
    "Eres AgroAsistente (preséntate siempre así al comienzo), un guía experto en agricultura, suelos, cultivos y prácticas agrícolas. "
    "Tu misión es orientar a campesinos y personas sin experiencia en el campo. "
    "Solo hablas de agricultura y temas relacionados como siembra, tipos de suelo, fertilizantes, clima, enfermedades de cultivos, conservación del suelo, etc. "
    "Si te preguntan algo fuera de estos temas, responde amablemente que no estás autorizado para hablar de eso. "
    "Háblame en un español colombiano y sencillo que pueda entender hasta la persona menos experta en el tema. "
    "Responde de forma clara, breve y con frases separadas. Usa párrafos cortos o listas. "
    "No excedas los 3 párrafos. Si la pregunta requiere una lista, usa viñetas."
)

# 🧾 Historial de conversación (se mantiene en memoria)
conversacion = [{"role": "system", "content": system_prompt}]

# 💬 Función para generar respuesta con contexto
def preguntar_agroasistente(pregunta):
    conversacion.append({"role": "user", "content": pregunta})

    respuesta = client.chat.completions.create(
        model="gpt-4",
        messages=conversacion,
        max_tokens=300
    )

    contenido = respuesta.choices[0].message.content
    conversacion.append({"role": "assistant", "content": contenido})

    # Limitar historial a los últimos 20 mensajes
    if len(conversacion) > 20:
        conversacion[:] = [conversacion[0]] + conversacion[-18:]

    return contenido

# 🌐 App Flask
app = Flask(__name__)

# 🖥️ Interfaz web
@app.route("/", methods=["GET", "POST"])
def index():
    respuesta = ""
    if request.method == "POST":
        pregunta = request.form["pregunta"]
        respuesta = preguntar_agroasistente(pregunta)
    return render_template("index.html", respuesta=respuesta)

# 🔄 API para peticiones externas
@app.route("/agrochat", methods=["POST"])
def agrochat():
    data = request.json
    pregunta = data.get("mensaje", "")
    respuesta = preguntar_agroasistente(pregunta)
    return jsonify({"respuesta": respuesta})

# 🏁 Ejecutar localmente (no necesario en Railway)
if __name__ == "__main__":
    app.run(debug=True)
