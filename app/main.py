from flask import Flask, render_template, request, redirect, jsonify
from google.cloud import vision, firestore
import os

app = Flask(__name__)
vision_client = vision.ImageAnnotatorClient()
db = firestore.Client()

PALABRAS_PROHIBIDAS = ['violencia', 'odio', 'sangre', 'grosería', 'borracho']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/subir', methods=['GET', 'POST'])
def subir():
    if request.method == 'POST':
        archivo = request.files['imagen']
        titulo = request.form.get('titulo')
        if not archivo:
            return render_template('error.html', mensaje='No se seleccionó imagen')
        contenido = archivo.read()
        response = vision_client.text_detection({'content': contenido})
        texto = response.text_annotations[0].description if response.text_annotations else ''
        encontradas = [p for p in PALABRAS_PROHIBIDAS if p in texto.lower()]
        edad = "12+" if encontradas else "6+"
        db.collection("librosClasificados").add({
            "titulo": titulo,
            "texto": texto,
            "edadSugerida": edad,
            "palabrasDetectadas": encontradas
        })
        return render_template('upload_photo.html', texto=texto, edad=edad, palabras=encontradas)
    return render_template('upload_photo.html')

@app.route('/buscar')
def buscar():
    docs = db.collection('librosClasificados').order_by('titulo').stream()
    resultados = [doc.to_dict() for doc in docs]
    return render_template('search.html', resultados=resultados)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
