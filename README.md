# Sistema de Reporte de Tiempos por Porcentaje de Dedicación

Aplicación web desarrollada en Python con Flask para registrar empleados, proyectos y reportes de dedicación porcentual.  
El sistema valida que cada empleado reporte exactamente el 100% de su dedicación por periodo y permite exportar los datos a CSV.

## 1. Tecnologías utilizadas

- Python: lenguaje principal del backend.
- Flask: framework web para crear rutas, vistas y lógica del sistema.
- SQLite: base de datos local.
- SQLAlchemy: ORM para trabajar con la base de datos usando clases de Python.
- HTML, CSS y JavaScript: frontend básico.
- CSV: formato de exportación de reportes.
- Gunicorn: servidor recomendado para despliegue.

## 2. Estructura del proyecto

```text
sistema_reporte_tiempos/
│
├── app.py
├── requirements.txt
├── README.md
├── exports/
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── templates/
    ├── base.html
    ├── index.html
    ├── login.html
    ├── dashboard.html
    ├── employees.html
    ├── projects.html
    ├── reports.html
    └── report_form.html
```

## 3. Instalación local

### Paso 1. Crear entorno virtual

En Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

En macOS o Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 3. Ejecutar la aplicación

```bash
python app.py
```

### Paso 4. Abrir en el navegador

```text
http://127.0.0.1:5000
```

## 4. Usuario de prueba

Al iniciar por primera vez, el sistema crea un usuario administrador:

```text
Correo: admin@empresa.com
Contraseña: admin123
Rol: administrador
```

## 5. Funcionalidades principales

### Autenticación
Permite iniciar sesión con correo y contraseña.

### Gestión de empleados
Permite registrar empleados con nombre, correo y rol.

### Gestión de proyectos
Permite crear proyectos activos o finalizados.

### Reporte de dedicación
Permite registrar el porcentaje de dedicación de un empleado a uno o varios proyectos durante un periodo.

### Validación automática
El sistema valida que la suma de los porcentajes sea exactamente 100%.

### Exportación
Permite descargar los reportes en formato CSV.

## 6. Despliegue en Render

### Paso 1. Subir el proyecto a GitHub

```bash
git init
git add .
git commit -m "Proyecto sistema reporte de tiempos"
git branch -M main
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

### Paso 2. Crear archivo Procfile

Este proyecto ya incluye el comando recomendado para Render mediante Gunicorn:

```bash
gunicorn app:app
```

En Render se debe configurar:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

### Paso 3. Crear Web Service

1. Ingresar a Render.
2. Seleccionar New Web Service.
3. Conectar el repositorio de GitHub.
4. Seleccionar Python.
5. Agregar los comandos anteriores.
6. Publicar.

## 7. Despliegue en PythonAnywhere

1. Subir los archivos del proyecto.
2. Crear entorno virtual.
3. Instalar dependencias con `pip install -r requirements.txt`.
4. Configurar una Web App tipo Flask.
5. Indicar el archivo `app.py`.
6. Reiniciar la aplicación.

## 8. Relación con los conceptos técnicos

- REST: se utiliza en rutas como `/api/projects` y `/api/reports`.
- Swagger: puede incorporarse posteriormente para documentar los endpoints REST.
- ReactJS: aunque este código usa plantillas HTML para facilitar ejecución, la arquitectura puede migrarse a React.
- Hooks: en una versión React se usarían para manejar estados y efectos.
- Context API: permitiría manejar sesión y roles globalmente.
- Axios: consumiría los endpoints REST desde React.
- Rutas y navegación: Flask maneja rutas del servidor; React Router podría manejar rutas del cliente.
- Despliegue: se realiza con Gunicorn y plataformas como Render o PythonAnywhere.
