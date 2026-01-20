import unittest
from calculo_de_probabilidad import *

class Test_normalizar_cadena(unittest.TestCase):

    def test_1(self):
        self.assertEqual(normalizar_cadena('Armando'), 'armando')

    def test_2(self):
        self.assertEqual(normalizar_cadena('armando'), 'armando')

    def test_3(self):
        self.assertEqual(normalizar_cadena(' armando'), 'armando')

    def test_4(self):
        self.assertEqual(normalizar_cadena('Iñigo'), 'iñigo')

    def test_5(self):
        self.assertEqual(normalizar_cadena('María Iñigo'), 'mariaiñigo')

class Test_calcular_probabilidades(unittest.TestCase):
    
    def test_1(self):
        lista_participantes = [Participante('Martínez', 'Gan', 'Sixto José'), Participante('Martínez', 'Gan', 'José Sixto')]
        calcular_probabilidades(lista_participantes)
        for participante, probabilidad_correcta in zip(lista_participantes, [0.3607681755829904, 0.6392318244170097]):
            self.assertEqual(participante.get_probabilidad(), probabilidad_correcta)

    def test_2(self):
        lista_participantes = [Participante('Mompó' , 'Gaspar'  , 'Jorge' ),
                               Participante('Mompó' , 'Gaspar'  , 'Diego' ),
                               Participante('Gaspar', 'Alós'    , 'Sofia' ),
                               Participante('Mompó' , 'Herreros', 'Daniel')]
        calcular_probabilidades(lista_participantes)
        for participante, probabilidad_correcta in zip(lista_participantes, [0.3607681755829904, 0.6392318244170097]):
            self.assertEqual(participante.get_probabilidad(), probabilidad_correcta)
if __name__ == '__main__':
    unittest.main(verbosity=2)