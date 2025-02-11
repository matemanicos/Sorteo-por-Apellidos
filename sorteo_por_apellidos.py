from enum import IntEnum
import os

import gspread
from oauth2client.service_account import ServiceAccountCredentials


class Atributos(IntEnum):

    PRIMER_APELLIDO  = 0
    SEGUNDO_APELLIDO = 1
    NOMBRE           = 2

class Letra(IntEnum):

    PRIMERA = 0
    SEGUNDA = 1


class Participante:
    """Representa a un participante del sorteo."""

    def __init__ (self, primer_apellido: str, segundo_apellido: str, nombre: str):

        self.ficha_nombre = [primer_apellido.lower(), segundo_apellido.lower(), nombre.lower()]
        if len(primer_apellido) == 0 or \
           len(segundo_apellido) == 0 or \
           len(nombre) == 0:
            raise ValueError('Se ha introducido un participante con alguno de sus atributos ---nombre, primer apellido o segundo apellido--- vacío.')
        
        self.probabilidad_de_ganar = -1
    
    
    def get_atributo (self, atributo: Atributos) -> str:
        """Devuelve el atributo `atributo` del participante."""

        return self.ficha_nombre[atributo]
    
    def get_probabilidad(self) -> float:
        """Devuelve la probabilidad de ganar del participante."""
        return self.probabilidad_de_ganar
    
    def set_probabilidad(self, p: float):
        """Asigna el valor `p` como la probabilidad de ganar del participante."""
        self.probabilidad_de_ganar = p

    def letra_atributo (self, letra: Letra, atributo: Atributos) -> str:
        """Devuelve la letra `letra` del atributo `atributo` del participante."""

        return self.get_atributo(atributo)[letra]
    
    def primeras_dos_letras (self, atributo: Atributos) -> str:
        """Devuelve las primeras dos letras del atributo `atributo` del participante."""

        return self.get_atributo(atributo)[0:2]

    def __str__ (self) -> str:
        """Escribe el nombre del participante como `primer apellido` `segundo apellido`, `nombre`."""

        return self.get_atributo(Atributos.PRIMER_APELLIDO).capitalize() + ' ' \
               + self.get_atributo(Atributos.SEGUNDO_APELLIDO).capitalize() + ', ' \
               + self.get_atributo(Atributos.NOMBRE).capitalize()
               
    def __repr__(self):
        return f"Participante('{self.apellido1}', '{self.apellido2}', '{self.nombre}')"
     

N_LETRAS = 26
VALOR_ULTIMA_LETRA  = ord('z') # Valor numérico ASCII de la letra z.
VALOR_PRIMERA_LETRA = ord('a') # Valor numérico ASCII de la letra a.

def distancia_lexicografica (a: str, b: str) -> int:
    """Dadas dos cadenas de texto `a` y `b`, devuelve la distancia lexicográfica entre ellas. Por ejemplo, `distancia_lexicografica('cy', 'cz') == 1` y `distancia_lexicografica('cy', 'da') == 2`."""

    # Garantiza que a < b.
    if a > b:
        a, b = b, a
    elif a == b:
        return 0
    
    distancia = 0

    len_a = len(a)
    len_b = len(b)

    longitud_comun = min(len_a, len_b)
    longitud_maxima = max(len_a, len_b)
    indice_maximo = longitud_maxima - 1

    # Encuentra el primer índice i de forma que a[i] != b[i].
    # En caso de que a[i] o b[i] no exista, el índice es el último valor
    # para el que a[i] y b[i] existen.
    try:
        indice_primera_diferencia = [a[i] == b[i] for i in range(longitud_comun)].index(False)

        # Hace lo de abajo, pero las cadenas que cuentaa deben ser de la
        # longitud máxima.
        aux = indice_maximo - indice_primera_diferencia
        distancia += (ord(b[indice_primera_diferencia]) - ord(a[indice_primera_diferencia]) - 1) * N_LETRAS**aux
        
    except ValueError:
        indice_primera_diferencia = longitud_comun - 1

    
    # Cuenta las cadenas de logitud máxima que coinciden hasta i-1 con a, pero
    # estando estrictamente entre a y b para i en el rango dado.
    for i in range(indice_primera_diferencia+1, len_a):
        distancia += (VALOR_ULTIMA_LETRA - ord(a[i])) * N_LETRAS**(indice_maximo - i)

    # Lo mismo pero con b.
    for i in range(indice_primera_diferencia+1, len_b):
        distancia += (ord(b[i]) - VALOR_PRIMERA_LETRA) * N_LETRAS**(indice_maximo - i)

    # La propia cadena b tiene que ser contada.
    distancia += 1

    return distancia
    

def calcular_probabilidades (participantes: list, atributo: Atributos = Atributos.PRIMER_APELLIDO, p_condicionada: float = 1):
    """Dada una lista de participantes `participantes` en el sorteo, devuelve una lista con las probabilidades de salir escogidos de cada uno."""
    
    # Ordenamos la lista en función del atributo que estemos comparando.
    participantes.sort(key = lambda x: x.get_atributo(atributo))

    # Si ya estamos comparando nombres, el proceso es distinto.
    if atributo != Atributos.NOMBRE:

        # Recorremos todos los participantes.
        i = 0
        while i < len(participantes):
            participante = participantes[i]

            # Si no es el primer participante y sus dos primeras letras
            # coinciden con el anterior.
            if i > 0 and participantes[i-1].primeras_dos_letras(atributo) == participante.primeras_dos_letras(atributo):
                participante.set_probabilidad(0)
                i += 1

            # En caso de que no sea el primero, sus primeras dos letras no
            # coincidiran con el anterior, ya que si no este lo hubiese
            # saltado.
            else:
                # Calculamos la probabilidad de que este apellido ganase.
                p = distancia_lexicografica(participantes[i-1].primeras_dos_letras(atributo), participante.primeras_dos_letras(atributo)) / N_LETRAS**2
                
                # Si es el primer participante, la distancia será la
                # complementaria, ya que después de 'zz' se pasa a 'aa'.
                if i == 0:
                    p = 1 - p

                # Vemos cuántos participantes más hay con el mismo atributo.
                n_participantes_iguales = 1 + [otro_participante.get_atributo(atributo) == participante.get_atributo(atributo) for otro_participante in participantes[i+1:]].count(True)
                
                # Si hay más de uno, se continuan los cálculos con el siguiente
                # atributo sobre dichos participantes.
                if n_participantes_iguales > 1:
                    calcular_probabilidades(participantes[i:i+n_participantes_iguales], atributo + 1, p)
                
                # Caso de que no, esta probabilidad es la de salir del
                # participante actual.
                else:
                    participante.set_probabilidad(p_condicionada * p)

                # Saltamos tantos índices como participantes con este apellido
                # hayamos estudiado.
                i += n_participantes_iguales

    # Si ya estamos estudiando el nombre, entonces el único que gana es el
    # primero por orden alfabético.                   
    else:

        participantes[0].set_probabilidad(p_condicionada)

        for participante in participantes[1:]:
            participante.set_probabilidad(0)
    


if __name__ == '__main__':   
    
    
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

    # Calcula las probabilidades de los participantes.
    # Dichas probabilidades quedan guardadas en los atributos de los objetos
    # Participante.
    calcular_probabilidades(lista_de_participantes)

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