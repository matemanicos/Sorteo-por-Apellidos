import os

from enum import Enum, unique, auto
from bidict import frozenbidict

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from calculos import *
from interfaz_de_usuario import *

PORTADA = """SORTEO POR APELLIDOS, por Matemañicos.
          
El sorteo por apellidos es un tipo de sorteo muy usado por la facilidad con la que este se implementa. Aunque existen numerosas variantes, solo trataremos una en este programa:
          
Se toman al azar dos letras del abecedario y se busca un apellido que empiece por esas dos letras o sea el primero en orden alfabético después de ellas. Una vez encontrado este apellido, si este es el primer apellido de más de una persona, se repite este sorteo entre las personas que lo comparten según su segundo apellido. Es decir, volvemos a tomar dos letras al azar y buscamos de la misma forma que antes entre los segundos apellidos. Si vuelve a haber más de una persona con el segundo apellido vencedor, repetiremos esto con los nombres.

Aunque pueda parecer un sorteo bien planteado, la realidad es muy distinta. Para ilustrar la injusticia de este sorteo y denunciar su uso en cualquier ámbito ponemos a su disposición este programa, para que puedan ver de primera mano el disparate en que consiste este sorteo. Para más información sobre el porqué de estas injusticias, visítese el artículo de Clara Grima: https://www.jotdown.es/2013/05/la-importancia-de-llamarse-grima/. 

El funcionamiento de este programa es muy simple:
   1) Se introduce una lista de nombres y apellidos al programa, ya sea a través de un formulario que ya viene integrado con este programa o escribiéndolo directamente.
   2) El programa desglosa las probabilidades de cada participante de ser seleccionado.
"""


@unique
class Modalidad_Introduccion_Datos (Enum):

    FORMULARIO = auto()
    A_MANO     = auto()

    SALIR      = auto()

def modalidad_introduccion_datos() -> Modalidad_Introduccion_Datos:

    RESPUESTAS_VALIDAS = frozenbidict({Modalidad_Introduccion_Datos.FORMULARIO : 'A', Modalidad_Introduccion_Datos.A_MANO : 'B'})
    print('¿Qué opción prefiere para introducir los datos?:\n   {0}) Utilizando el formulario de Google (recomendado para grupos grandes).\n   {1}) Introduciendo los nombres y apellidos a través del teclado.'.format(*RESPUESTAS_VALIDAS.values()))

    
    for intentos in range(10):
        try:
            respuesta = input('Introduzca <<{0}>> o <<{1}>>: '.format(*RESPUESTAS_VALIDAS.values()))
            return RESPUESTAS_VALIDAS.inverse[respuesta]
        
        except:
            print('La respuesta que ha dado no es válida. Inténtelo de nuevo.')

    raise Exception('Número de intentos máximo excedido.') # Dar más estructura a las excepciones.

def pedir_atributo (atributo) -> str:

    respuesta = input('Introduce el {0}: '.format(atributo))

    return respuesta

@unique
class Respuesta_Si_No (Enum):

    NO = auto()
    SI = auto()

def quiere_mas_participantes () -> bool:

    RESPUESTAS_VALIDAS = frozenbidict({Respuesta_Si_No.NO : 'N', Respuesta_Si_No.SI : 'S'})
    print('¿Desea introducir más participantes?')

    for intentos in range(10):
        respuesta = input('Responda <<{respuesta_si}>> si es que sí o <<{respuesta_no}>> si es que no: '.format(respuesta_si = RESPUESTAS_VALIDAS[Respuesta_Si_No.SI], respuesta_no = RESPUESTAS_VALIDAS[Respuesta_Si_No.NO]))

        if respuesta == RESPUESTAS_VALIDAS[Respuesta_Si_No.NO]:
            return False
        elif respuesta == RESPUESTAS_VALIDAS[Respuesta_Si_No.SI]:
            return True
        else:
            print('La respuesta que ha dado no es válida. Inténtelo de nuevo.')

    raise Exception('Número de intentos máximo excedido.') # Dar más estructura a las excepciones.

def quiere_introducir_otra_lista () -> bool:

    RESPUESTAS_VALIDAS = frozenbidict({Respuesta_Si_No.NO : 'N', Respuesta_Si_No.SI : 'S'})
    print('¿Desea introducir una nueva lista?')

    for intentos in range(10):
        respuesta = input('Responda <<{respuesta_si}>> si es que sí o <<{respuesta_no}>> si es que no: '.format(respuesta_si = RESPUESTAS_VALIDAS[Respuesta_Si_No.SI], respuesta_no = RESPUESTAS_VALIDAS[Respuesta_Si_No.NO]))

        if respuesta == RESPUESTAS_VALIDAS[Respuesta_Si_No.NO]:
            return False
        elif respuesta == RESPUESTAS_VALIDAS[Respuesta_Si_No.SI]:
            return True
        else:
            print('La respuesta que ha dado no es válida. Inténtelo de nuevo.')

    raise Exception('Número de intentos máximo excedido.') # Dar más estructura a las excepciones.


# Juntar ambas en una función que haga preguntas sí o no.
def obtener_lista_formulario () -> list[Participante]:

    # Configurar la conexión con Google Sheets
    scope = ["https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"]
    credenciales = ServiceAccountCredentials.from_json_keyfile_name(
        os.path.join(os.path.dirname(os.path.abspath(__file__)),"credentials.json"), scope)
    cliente = gspread.authorize(credenciales)
    
    # Abre el Google Sheets y selecciona la hoja
    # Cambia por el nombre real de tu Google Sheet
    spreadsheet = cliente.open_by_key("1R7wk0Y_wONLVzKe_PjaDbg6GaA-XNtLTtnwzhNJYeiU")
    hoja = spreadsheet.sheet1  # Selecciona la primera hoja
    
    # Obtener los datos (suponiendo que están en columnas: Nombre, Apellido1, Apellido2)
    datos_prov = hoja.get_all_values()
    
    ## elimina las líneas sin datos
    i=1
    for dato in datos_prov:
        if dato[0] == '':
            i+=1
            
    datos = datos_prov[i:]
    
    # Convertir los datos en objetos Participante con el formato correcto
    lista_de_participantes = [Participante(apellido1, apellido2, nombre)
                    for fecha, nombre, apellido1, apellido2 in datos]
    
    return lista_de_participantes

def obtener_lista_a_mano () -> list[Participante]:

    lista_de_participantes = list()

    quiere_otro_participante = True

    while quiere_otro_participante:

        primer_apellido  = pedir_atributo(Atributos.PRIMER_APELLIDO)
        segundo_apellido = pedir_atributo(Atributos.SEGUNDO_APELLIDO)
        nombre           = pedir_atributo(Atributos.NOMBRE)

        lista_de_participantes.append(Participante(primer_apellido, segundo_apellido, nombre))

        quiere_otro_participante = quiere_mas_participantes()

    return lista_de_participantes

def imprimir_tabla (lista_de_participantes: list[Participante]) -> None:

    # Ordenamos la lista por orden alfabético.
    lista_de_participantes.sort(key = lambda x : str(x))

    # Imprimimos la tabla.
    caracter_linea = '-'
    longitud_linea = 100
    print('\n')
    print(caracter_linea * longitud_linea)
    for participante in lista_de_participantes:
        print('{0:<30} : {1:>6.3f} %'.format(str(participante), participante.get_probabilidad() * 100))
    print(caracter_linea * longitud_linea)
    print('\n')

if __name__ == '__main__':   
    
    print(PORTADA)
    
    continuar_en_el_programa = True
    while continuar_en_el_programa:

        respuesta_modalidad_introduccion_datos = modalidad_introduccion_datos()
        if respuesta_modalidad_introduccion_datos == Modalidad_Introduccion_Datos.SALIR:
            
            continuar_en_el_programa = False

        else:
            if respuesta_modalidad_introduccion_datos == Modalidad_Introduccion_Datos.FORMULARIO:

                lista_de_participantes = obtener_lista_formulario()

            elif respuesta_modalidad_introduccion_datos == Modalidad_Introduccion_Datos.A_MANO:
                
                lista_de_participantes = obtener_lista_a_mano()
            
            else:
                raise Exception('Hay una opción de introducción de datos ofertada pero no implementada.')

            # Calcula las probabilidades de los participantes.
            # Dichas probabilidades quedan guardadas en los atributos de los objetos
            # Participante.
            calcular_probabilidades(lista_de_participantes)

            imprimir_tabla(lista_de_participantes)

            if not quiere_introducir_otra_lista():
                continuar_en_el_programa = False