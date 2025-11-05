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
    """
    Obtiene las respuestas desde la Forms API asegurando la asignación
    correcta nombre / apellido1 / apellido2 utilizando los títulos de
    las preguntas del propio formulario como fuente de verdad.
    """
    participantes = []

    # 1) Obtener la estructura del formulario para mapear questionId -> título
    try:
        form = forms_service.forms().get(formId=form_id).execute()
    except Exception as e:
        print("Error obteniendo la estructura del formulario:", e)
        return participantes

    qid_to_title = {}
    items = form.get("items", []) or []
    for item in items:
        # extraer título y questionId si existe
        title = item.get("title", "") or item.get("label", "")
        q = item.get("questionItem", {}).get("question", {})
        qid = q.get("questionId") or item.get("itemId")
        if qid:
            qid_to_title[str(qid)] = title.strip().lower()

    # 2) Obtener respuestas
    try:
        resp = forms_service.forms().responses().list(formId=form_id).execute()
    except Exception as e:
        print("Error obteniendo respuestas:", e)
        return participantes

    for r in resp.get("responses", []):
        answers = r.get("answers", {}) or {}

        # campos por defecto vacíos
        nombre = ""
        apellido1 = ""
        apellido2 = ""

        # 3) Primero: intentar asignar por título asociado al questionId
        for qid, answer_obj in answers.items():
            text = ""
            # extraer texto de la respuesta (varios formatos posibles)
            if "textAnswers" in answer_obj:
                arr = answer_obj["textAnswers"].get("answers", [])
                if arr:
                    text = arr[0].get("value", "").strip()
            elif "textAnswer" in answer_obj:  # por si hay variantes
                text = str(answer_obj.get("textAnswer", "")).strip()
            else:
                # fallback sobre cualquier campo 'value'
                # (por si alguna respuesta viene en otro formato)
                for v in answer_obj.values():
                    if isinstance(v, str) and v.strip():
                        text = v.strip()
                        break

            title = qid_to_title.get(str(qid), "").lower()

            # heurística por palabras clave en el título
            if "nombre" in title or "name" in title:
                nombre = text if text else nombre
            elif "apellido 1" in title or "primer apellido" in title or "apellido1" in title or "apellido 1" in title:
                apellido1 = text if text else apellido1
            elif "apellido 2" in title or "segundo apellido" in title or "apellido2" in title:
                apellido2 = text if text else apellido2
            else:
                # si el título no ayuda, intentar detectar por el contenido (poco fiable)
                # ej. si parece un nombre (inicial mayúscula sin espacios largos)
                if not nombre and text and " " in text and len(text.split()) >= 2:
                    # si hay dos palabras, quizá sea "Nombre Apellido" -> tomar primera como nombre
                    nombre = text.split()[0]
                elif not nombre and not apellido1 and text:
                    # asignar provisionalmente en orden de aparición
                    if not nombre:
                        nombre = text
                    elif not apellido1:
                        apellido1 = text
                    else:
                        apellido2 = text

        # 4) Fallback: si no se detectó por títulos, usar el orden de aparición de answers
        if not (nombre and apellido1):
            vals = []
            for qid, answer_obj in answers.items():
                arr = answer_obj.get("textAnswers", {}).get("answers", [])
                if arr:
                    v = arr[0].get("value", "").strip()
                    if v:
                        vals.append(v)
            # intentar mapear [fecha?] nombre ap1 ap2  -> buscamos por el patrón más común
            if len(vals) >= 3:
                # si hay 4 y la primera es fecha, muchas hojas incluyen timestamp; asumir vals[-3],[-2],[-1]
                nombre = nombre or vals[-3]
                apellido1 = apellido1 or vals[-2]
                apellido2 = apellido2 or vals[-1]
            elif len(vals) == 2:
                nombre = nombre or vals[0]
                apellido1 = apellido1 or vals[1]
            elif len(vals) == 1:
                nombre = nombre or vals[0]

        participantes.append(Participante(apellido1, apellido2, nombre))

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
            

