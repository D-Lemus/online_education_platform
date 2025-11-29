# client_common.py
import json
import requests

API_URL = "http://127.0.0.1:8001"


def safe_print_response(response: requests.Response):
    """Imprime la respuesta sin crashear cuando no es JSON."""
    print("Status code:", response.status_code)
    try:
        data = response.json()
        print("JSON:", json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("El servidor no devolvió JSON. Cuerpo bruto:")
        print(response.text)


# ---------- USUARIOS ----------

def create_user_cli():
    print("\n=== Crear Usuario ===")
    email = input("Email: ")
    full_name = input("Nombre completo: ")
    password = input("Contraseña: ")
    role = input("Rol (Student/Teacher) [Student]: ") or "Student"

    payload = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": role
    }

    response = requests.post(f"{API_URL}/users/", json=payload)
    safe_print_response(response)


def login_cli():
    """
    Intenta iniciar sesión.
    Si tiene éxito, devuelve un dict con la info del usuario (email, full_name, role).
    Si falla, devuelve None.
    """
    print("\n=== Iniciar sesión ===")
    email = input("Email: ")
    password = input("Contraseña: ")

    payload = {"email": email, "password": password}
    response = requests.post(f"{API_URL}/users/login", json=payload)

    print("Status code:", response.status_code)
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Respuesta no es JSON:")
        print(response.text)
        return None

    if response.status_code != 200:
        print("Error al iniciar sesión:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return None

    # Debe regresar: { "email": ..., "full_name": ..., "role": ... }
    print("\nLogin correcto. Usuario:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def update_user_cli(current_email: str) -> dict | None:
    """
    Actualiza el usuario con email current_email usando tu endpoint PUT /users/{email}.
    Regresa un dict con los datos actualizados (email/full_name/role) o None si falló.
    """
    print("\n=== Actualizar usuario ===")
    print(f"Email actual: {current_email}")

    print("¿Qué quieres actualizar?")
    print("1) Solo email")
    print("2) Solo nombre")
    print("3) Email y nombre")
    print("4) Cancelar")

    choice = input("Opción: ")

    new_email = None
    new_full_name = None

    if choice == "1":
        new_email = input("Introduce el nuevo email: ")
    elif choice == "2":
        new_full_name = input("Introduce el nuevo nombre: ")
    elif choice == "3":
        new_email = input("Introduce el nuevo email: ")
        new_full_name = input("Introduce el nuevo nombre: ")
    elif choice == "4":
        print("Actualización cancelada.")
        return None
    else:
        print("Opción no válida. No se actualizó nada.")
        return None

    # Construimos el JSON solo con los campos que sí se quieran cambiar
    payload: dict = {}
    if new_email:
        payload["email"] = new_email
    if new_full_name:
        payload["full_name"] = new_full_name

    if not payload:
        print("No se proporcionaron datos para actualizar.")
        return None

    response = requests.put(
        f"{API_URL}/users/{current_email}",
        json=payload
    )

    print("Status code:", response.status_code)
    try:
        data = response.json()
        print("Respuesta actualización:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("La respuesta no es JSON:")
        print(response.text)
        return None

    if response.status_code != 200:
        print("No se pudo actualizar el usuario.")
        return None

    # Actualizamos el email localmente si cambió
    updated_email = data.get("email", current_email)
    updated_full_name = data.get("full_name", "")
    updated_role = data.get("role", "Student")

    return {
        "email": updated_email,
        "full_name": updated_full_name,
        "role": updated_role,
    }


# ---------- CURSOS Y LECCIONES ----------

def list_courses_cli():
    print("\n=== Listar cursos ===")
    response = requests.get(f"{API_URL}/courses/")
    safe_print_response(response)


def create_course_cli():
    print("\n=== Crear Curso ===")
    course_name = input("Nombre del curso: ")
    taught_by = input("Profesor: ")

    payload = {
        "course_name": course_name,
        "taught_by": taught_by
    }

    response = requests.post(f"{API_URL}/courses/", json=payload)
    safe_print_response(response)


def create_lesson_cli():
    print("\n=== Crear Lección ===")
    course_id = input("ID del curso: ")
    title = input("Título: ")
    content = input("Contenido: ")
    order = int(input("Orden (1,2,3...): "))

    payload = {
        "title": title,
        "content": content,
        "order": order
    }

    response = requests.post(f"{API_URL}/courses/{course_id}/lessons", json=payload)
    safe_print_response(response)


def list_lessons_cli():
    print("\n=== Listar lecciones de un curso ===")
    course_id = input("ID del curso: ")
    response = requests.get(f"{API_URL}/courses/{course_id}/lessons")
    safe_print_response(response)


# ---------- ADMIN (USUARIOS) ----------

def list_users_cli():
    print("\n=== Listar usuarios ===")
    response = requests.get(f"{API_URL}/users/")
    safe_print_response(response)
