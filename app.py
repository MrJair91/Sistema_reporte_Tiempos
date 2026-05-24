"""
Sistema de Reporte de Tiempos por Porcentaje de Dedicación
----------------------------------------------------------

Este archivo contiene todo el backend de la aplicación.

Explicación general:
- Flask crea el servidor web.
- SQLAlchemy conecta Python con SQLite mediante modelos.
- Las rutas renderizan páginas HTML y también exponen endpoints REST.
- El sistema valida que los porcentajes reportados por periodo sumen exactamente 100%.
- Se incluye exportación CSV para análisis administrativo.

Para ejecutar:
    python app.py
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import csv
import io
from datetime import datetime

# Instancia principal de Flask.
# __name__ permite que Flask encuentre correctamente carpetas como templates y static.
app = Flask(__name__)

# Clave secreta usada para manejar sesiones de usuario.
# En producción debe reemplazarse por una variable de entorno segura.
app.config["SECRET_KEY"] = "clave-secreta-cambiar-en-produccion"

# Configuración de SQLite.
# El archivo sistema_tiempos.db se crea automáticamente al ejecutar la aplicación.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sistema_tiempos.db"

# Desactiva rastreo innecesario de cambios para mejorar rendimiento.
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# SQLAlchemy permite definir tablas como clases de Python.
db = SQLAlchemy(app)


# ==========================
# MODELOS DE BASE DE DATOS
# ==========================

class User(db.Model):
    """
    Modelo de usuario.

    Representa empleados, líderes de proyecto y administradores.
    Cada usuario tiene un rol que controla sus permisos dentro del sistema.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="empleado")

    def set_password(self, password):
        """
        Convierte la contraseña en un hash seguro.
        No se recomienda guardar contraseñas en texto plano.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Compara la contraseña ingresada con el hash almacenado.
        """
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    """
    Modelo de proyecto.

    Permite registrar proyectos activos o finalizados.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Activo")


class TimeReport(db.Model):
    """
    Modelo de reporte de dedicación.

    Cada registro representa el porcentaje de dedicación de un empleado
    a un proyecto específico durante un periodo determinado.
    """
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    period = db.Column(db.String(40), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    observations = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employee = db.relationship("User", backref="reports")
    project = db.relationship("Project", backref="reports")


# ==========================
# DECORADORES DE SEGURIDAD
# ==========================

def login_required(view_function):
    """
    Decorador que protege rutas privadas.

    Si el usuario no ha iniciado sesión, se redirige a la pantalla de login.
    """
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para acceder.", "warning")
            return redirect(url_for("login"))
        return view_function(*args, **kwargs)
    return wrapper


def admin_required(view_function):
    """
    Decorador para rutas administrativas.

    Solo usuarios con rol administrador pueden acceder.
    """
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if session.get("role") != "administrador":
            flash("No tienes permisos para esta acción.", "danger")
            return redirect(url_for("dashboard"))
        return view_function(*args, **kwargs)
    return wrapper


# ==========================
# RUTAS WEB
# ==========================

@app.route("/")
def index():
    """
    Página inicial del sistema.
    """
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Ruta de autenticación.

    GET: muestra el formulario.
    POST: valida correo y contraseña.
    """
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.id
            session["name"] = user.name
            session["role"] = user.role
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for("dashboard"))

        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Cierra la sesión actual.
    """
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """
    Panel principal.

    Muestra indicadores básicos:
    - Total de empleados.
    - Total de proyectos.
    - Total de reportes registrados.
    """
    employees_count = User.query.count()
    projects_count = Project.query.count()
    reports_count = TimeReport.query.count()

    return render_template(
        "dashboard.html",
        employees_count=employees_count,
        projects_count=projects_count,
        reports_count=reports_count
    )


@app.route("/employees", methods=["GET", "POST"])
@login_required
@admin_required
def employees():
    """
    Gestión de empleados.

    Permite crear usuarios con rol:
    - administrador
    - líder de proyecto
    - empleado
    """
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        role = request.form.get("role")
        password = request.form.get("password")

        if User.query.filter_by(email=email).first():
            flash("Ya existe un usuario con ese correo.", "danger")
            return redirect(url_for("employees"))

        user = User(name=name, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Empleado creado correctamente.", "success")
        return redirect(url_for("employees"))

    users = User.query.order_by(User.name.asc()).all()
    return render_template("employees.html", users=users)


@app.route("/projects", methods=["GET", "POST"])
@login_required
def projects():
    """
    Gestión de proyectos.

    Permite registrar proyectos con nombre, descripción y estado.
    """
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        status = request.form.get("status")

        project = Project(name=name, description=description, status=status)

        db.session.add(project)
        db.session.commit()

        flash("Proyecto creado correctamente.", "success")
        return redirect(url_for("projects"))

    projects_list = Project.query.order_by(Project.name.asc()).all()
    return render_template("projects.html", projects=projects_list)


@app.route("/reports")
@login_required
def reports():
    """
    Consulta de reportes registrados.
    """
    reports_list = TimeReport.query.order_by(TimeReport.created_at.desc()).all()
    return render_template("reports.html", reports=reports_list)


@app.route("/reports/new", methods=["GET", "POST"])
@login_required
def new_report():
    """
    Registro de reporte de dedicación.

    La lógica central valida que el total de porcentajes enviados
    para un empleado y periodo sea exactamente 100%.
    """
    employees = User.query.order_by(User.name.asc()).all()
    projects_list = Project.query.filter_by(status="Activo").order_by(Project.name.asc()).all()

    if request.method == "POST":
        employee_id = int(request.form.get("employee_id"))
        period = request.form.get("period")
        observations = request.form.get("observations")

        project_ids = request.form.getlist("project_id")
        percentages = request.form.getlist("percentage")

        clean_rows = []
        total = 0

        for project_id, percentage in zip(project_ids, percentages):
            if project_id and percentage:
                value = float(percentage)
                total += value
                clean_rows.append((int(project_id), value))

        # Validación del alcance funcional:
        # La suma de dedicación por periodo debe ser exactamente 100%.
        if round(total, 2) != 100:
            flash(f"La suma de los porcentajes debe ser 100%. Total actual: {total}%.", "danger")
            return redirect(url_for("new_report"))

        # Evita duplicar reportes del mismo empleado en el mismo periodo.
        existing = TimeReport.query.filter_by(employee_id=employee_id, period=period).all()
        for item in existing:
            db.session.delete(item)

        for project_id, value in clean_rows:
            report = TimeReport(
                employee_id=employee_id,
                project_id=project_id,
                period=period,
                percentage=value,
                observations=observations
            )
            db.session.add(report)

        db.session.commit()
        flash("Reporte registrado correctamente.", "success")
        return redirect(url_for("reports"))

    return render_template("report_form.html", employees=employees, projects=projects_list)


@app.route("/reports/export")
@login_required
def export_reports():
    """
    Exporta los reportes en CSV.

    CSV es útil porque puede abrirse en Excel, Google Sheets o sistemas contables.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Empleado", "Correo", "Rol", "Proyecto", "Periodo", "Porcentaje", "Observaciones", "Fecha de creación"])

    reports_list = TimeReport.query.order_by(TimeReport.created_at.desc()).all()

    for report in reports_list:
        writer.writerow([
            report.employee.name,
            report.employee.email,
            report.employee.role,
            report.project.name,
            report.period,
            report.percentage,
            report.observations or "",
            report.created_at.strftime("%Y-%m-%d %H:%M")
        ])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=reportes_dedicacion.csv"
    return response


# ==========================
# ENDPOINTS REST
# ==========================

@app.route("/api/projects", methods=["GET"])
def api_projects():
    """
    Endpoint REST tipo GET.

    Funcionalidad:
    Devuelve los proyectos en formato JSON.
    Este endpoint podría ser consumido desde React usando Axios.
    """
    projects_list = Project.query.all()
    return jsonify([
        {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status
        }
        for project in projects_list
    ])


@app.route("/api/reports", methods=["GET"])
def api_reports():
    """
    Endpoint REST tipo GET.

    Funcionalidad:
    Devuelve los reportes registrados en formato JSON.
    """
    reports_list = TimeReport.query.all()
    return jsonify([
        {
            "id": report.id,
            "employee": report.employee.name,
            "project": report.project.name,
            "period": report.period,
            "percentage": report.percentage,
            "observations": report.observations
        }
        for report in reports_list
    ])


# ==========================
# INICIALIZACIÓN
# ==========================

def create_initial_data():
    """
    Crea datos iniciales para probar el sistema.

    Se ejecuta solo si no existen usuarios.
    """
    if User.query.count() == 0:
        admin = User(
            name="Administrador del Sistema",
            email="admin@empresa.com",
            role="administrador"
        )
        admin.set_password("admin123")

        employee = User(
            name="Empleado de Prueba",
            email="empleado@empresa.com",
            role="empleado"
        )
        employee.set_password("empleado123")

        project_a = Project(
            name="Proyecto Ingeniería Norte",
            description="Proyecto de ingeniería y construcción zona norte.",
            status="Activo"
        )

        project_b = Project(
            name="Proyecto Construcción Sur",
            description="Proyecto de construcción zona sur.",
            status="Activo"
        )

        db.session.add_all([admin, employee, project_a, project_b])
        db.session.commit()


with app.app_context():
    db.create_all()
    create_initial_data()


if __name__ == "__main__":
    # debug=True permite ver errores durante desarrollo.
    # En producción debe ejecutarse con Gunicorn.
    app.run(debug=True)
