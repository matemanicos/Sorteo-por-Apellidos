from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import qrcode
from PIL import Image
import time, sys

from calculos import Participante, calcular_probabilidades
from sorteo_por_apellidos import imprimir_tabla

# Autenticación con la cuenta de servicio
SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPES)
except FileNotFoundError:
    print("Error de autenticación. Compruebe que el archivo credentials.json está en el directorio scrpits. Si el error persiste, contacte con matemanicos@unizar.es .")
    sys.exit()

# Conectar con la API de Drive y Forms
drive_service = build("drive", "v3", credentials=creds)
forms_service = build("forms", "v1", credentials=creds)

def generar_qr(url):
    """Genera un código QR a partir de una URL y lo muestra en pantalla."""
    qr = qrcode.QRCode(
        version=1,  # Tamaño del QR (1 es el más pequeño)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # Nivel de corrección de errores
        box_size=10,  # Tamaño de cada caja del QR
        border=4  # Bordes del QR
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white").convert("RGB")  # Convertir a imagen PIL
    img.show()
    
    return url

def crear_formulario():
    """Crea el formulario para introducir participantes."""
    form_metadata = {"info": {"title": "Sorteo por apellidos"}}
    form = forms_service.forms().create(body=form_metadata).execute()
    
    preguntas = {
        "requests": [
            {"createItem": {"item": {"title": "Nombre", "questionItem": {"question": {"required": True, "textQuestion": {}}}}, "location": {"index": 0}}},
            {"createItem": {"item": {"title": "Apellido 1", "questionItem": {"question": {"required": True, "textQuestion": {}}}}, "location": {"index": 1}}},
            {"createItem": {"item": {"title": "Apellido 2", "questionItem": {"question": {"required": True, "textQuestion": {}}}}, "location": {"index": 2}}}
        ]
    }
    forms_service.forms().batchUpdate(formId=form["formId"], body=preguntas).execute()
    print("Formulario creado:", form["responderUri"])
    try:
        generar_qr(form["responderUri"])
    except:
        print("Se ha producido un error. Si el error persiste, contacte con matemanicos@unizar.es .")
        eliminar_formulario(form["formId"])
        sys.exit()
    return form["formId"], form["responderUri"]

def obtener_respuestas(form_id):
    """Obtiene las respuestas directamente desde Google Forms y las formatea."""
    responses = forms_service.forms().responses().list(formId=form_id).execute()
    participantes = []
    
    if "responses" in responses:
        for response in responses["responses"]:
            answers = iter(response.get("answers", {}).items())
            nombre = next(answers)[1].get("textAnswers", {}).get("answers", [{}])[0].get("value", "")
            apellido1 = next(answers)[1].get("textAnswers", {}).get("answers", [{}])[0].get("value", "")
            apellido2 = next(answers)[1].get("textAnswers", {}).get("answers", [{}])[0].get("value", "")
            participantes.append(Participante(apellido1,apellido2,nombre))
    
    return participantes

def eliminar_formulario(form_id):
    """Elimina el formulario de Google Drive."""
    drive_service.files().delete(fileId=form_id).execute()
    print("Formulario eliminado.\n")

def obtener_lista_formulario():
    """"Interfaz de usuario para extraer las respuestas del formulario o borrarlo y terminar con la actividad"""
    print()
    form_id, form_url = crear_formulario()
    
    print("Presiona 'Enter' para obtener respuestas o 'q' para salir y eliminar el formulario.")
    while True:
        try:
            tecla = input("[Enter] Obtener respuestas | [q] Salir y borrar formulario: ")
            if tecla.lower() == 'q':
                eliminar_formulario(form_id)
                break
            else:
                lista_de_participantes = obtener_respuestas(form_id)
                calcular_probabilidades(lista_de_participantes)
                imprimir_tabla(lista_de_participantes)
        except:
            print("Se ha producido un error. Si el error persiste, contacte con matemanicos@unizar.es .")
            eliminar_formulario(form_id)
            sys.exit()
            
    return
            

