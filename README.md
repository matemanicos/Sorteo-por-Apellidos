
# Simulador de sorteo por apellidos

Este proyecto implementa un **simulador del sorteo por apellidos**, un método de selección ampliamente utilizado por su aparente simplicidad, pero que presenta **importantes sesgos e injusticias matemáticas**.

El objetivo del programa es **calcular y mostrar la probabilidad real** de que cada participante resulte seleccionado, evidenciando la desigualdad inherente a este tipo de sorteos.

El proyecto está desarrollado con **Flask (Python)** y ofrece una interfaz web sencilla e intuitiva.

---

## 📌 ¿En qué consiste el sorteo por apellidos?

El sorteo funciona del siguiente modo:

1. Se eligen **dos letras al azar** del alfabeto.
2. Se selecciona a la **primera persona en orden alfabético** cuyo **primer apellido** empiece por esas letras o sea el primero posterior.
3. Si hay empate (mismo primer apellido), se repite el proceso con el **segundo apellido**.
4. Si el empate persiste, se repite con el **nombre**.

Aunque parece un método neutral, en realidad introduce **sesgos muy fuertes** que favorecen a ciertos apellidos.

Para una explicación divulgativa del problema, puede consultarse el artículo de Clara Grima:  
https://www.jotdown.es/2013/05/la-importancia-de-llamarse-grima/

---

## 🧮 Funcionalidades principales

- Introducción manual de participantes (nombre y dos apellidos)
- Importación de participantes mediante **Google Forms**, accesible vía **QR**
- Cálculo exacto de probabilidades según el algoritmo del sorteo
- Visualización gráfica de probabilidades
- Interfaz clara y responsive
- Eliminación automática del formulario de Google Forms tras la extracción

---

## 🛠️ Tecnologías utilizadas

- Python 3
- Flask
- HTML + CSS
- Google Forms API
- Google Drive API
- qrcode
- unidecode

---

## 📁 Estructura del proyecto

```
.
├── main.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── get-player-from-form.html
│   └── display-probabilities.html
├── static/
│   ├── css/
│   │   └── styles.css
│   └── images/
│       └── logo.png
├── scripts/
│   ├── api.py
│   └── calculo_de_probabilidad.py
└── README.md
```

---

## 🚀 Instalación y ejecución

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/simulador-sorteo-apellidos.git
cd simulador-sorteo-apellidos
```

### 2️⃣ Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Instalar dependencias

```bash
pip install flask google-api-python-client oauth2client gspread qrcode[pil] unidecode
```

### 4️⃣ Configurar credenciales de Google

- Crear una **cuenta de servicio** en Google Cloud
- Habilitar:
  - Google Forms API
  - Google Drive API
- Descargar el archivo de credenciales como:

```
scripts/credentials.json
```

---

### 5️⃣ Ejecutar la aplicación

```bash
python main.py
```

La aplicación estará disponible en:

```
http://127.0.0.1:5000
```

---

## 📊 Cálculo de probabilidades

El núcleo matemático se encuentra en:

```
scripts/calculo_de_probabilidad.py
```

El algoritmo:
- Ordena lexicográficamente a los participantes
- Calcula distancias entre combinaciones de letras
- Evalúa probabilidades condicionadas en caso de empates
- Produce probabilidades exactas, no simuladas

---

## ⚖️ Licencia

Este proyecto se distribuye bajo la licencia:

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)**

https://creativecommons.org/licenses/by-nc-sa/4.0/

---

## 👤 Autoría y contacto

Proyecto desarrollado con fines **educativos y divulgativos**.

Para dudas o incidencias relacionadas con el uso académico del proyecto:  
📧 matemanicos@unizar.es
