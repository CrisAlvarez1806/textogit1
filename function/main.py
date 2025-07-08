from google.cloud import vision
from google.cloud import firestore
import base64

def procesar_imagen(request):
    request_json = request.get_json(silent=True)
    if not request_json or 'imagen_base64' not in request_json:
        return {"error": "Campo 'imagen_base64' faltante"}, 400

    content = base64.b64decode(request_json['imagen_base64'])
    vision_client = vision.ImageAnnotatorClient()
    db = firestore.Client()

    result = vision_client.text_detection({'content': content})
    texto = result.text_annotations[0].description if result.text_annotations else ''

    palabras = ['violencia', 'odio', 'sangre']
    encontradas = [p for p in palabras if p in texto.lower()]
    edad = "12+" if encontradas else "6+"

    db.collection("librosClasificados").add({
        "texto": texto,
        "palabrasDetectadas": encontradas,
        "edadSugerida": edad
    })

    return {"texto": texto, "edad": edad, "palabras": encontradas}
