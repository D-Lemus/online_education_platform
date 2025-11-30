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

#===================================== Courses and Lessons =====================================================
def list_courses_cli():
    """
    List all courses
    """
    print("\n=== Listar cursos ===")
    response = requests.get(f"{API_URL}/courses/")
    safe_print_response(response)

def list_my_courses_cli(current_user_email: str):
    """
    List the courses the user is enroleld in
    """
    print("\n=== My courses ===")
    response = requests.get(f"{API_URL}/courses/by-teacher/{current_user_email}")
    safe_print_response(response)


def create_course_cli(current_user_email: str):
    """
    Creates a course
    """
    print("\n=== Create Course ===")
    course_name = input("Course Name: ")

    payload = {
        "course_name": course_name,
        "taught_by": current_user_email
    }

    response = requests.post(f"{API_URL}/courses/", json=payload)
    safe_print_response(response)


def create_lesson_cli():
    """
    Crea una leccion
    """
    print("\n=== Crear Lección ===")
    course_id = select_course_cli()
    title = input("Título: ")
    content = input("Contenido: ")
    while True:
        try:
            order = int(input("Orden (1,2,3...): "))
            break
        except ValueError:
            print("Please put a valid number for the order.")
    payload = {
        "title": title,
        "content": content,
        "order": order
    }

    response = requests.post(f"{API_URL}/courses/{course_id}/lessons", json=payload)
    safe_print_response(response)


def list_lessons_cli(current_user_email: str):
    """
    Lista las lecciones de un curso.
    """
    print("\n=== Listar lecciones de un curso ===")
    list_my_courses_cli(current_user_email)
    course_id = select_course_cli()
    response = requests.get(f"{API_URL}/courses/{course_id}/lessons")
    safe_print_response(response)



def select_course_cli() -> str | None:
    """
    Shows all the courses and makes the user choose one
    """
    print("\n=== Seleccionar curso ===")
    response = requests.get(f"{API_URL}/courses/")

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: la respuesta de /courses/ no es JSON.")
        print(response.text)
        return None

    if not isinstance(data, list) or len(data) == 0:
        print("No hay cursos disponibles.")
        return None

    # Mostrar cursos numerados
    for idx, course in enumerate(data, start=1):
        name = course.get("course_name", "sin nombre")
        taught_by = course.get("taught_by", "desconocido")
        print(f"{idx}) {name}  (Profesor: {taught_by})")

    choice = input("Elige un curso por número: ")
    if not choice.isdigit():
        print("Opción no válida.")
        return None

    choice_idx = int(choice)
    if choice_idx < 1 or choice_idx > len(data):
        print("Número fuera de rango.")
        return None

    selected_course = data[choice_idx - 1]
    course_id = str(selected_course.get("_id") or selected_course.get("id"))
    if not course_id:
        print("No se encontró el ID del curso.")
        return None

    return course_id

def select_lesson_cli(course_id: str) -> str | None:
    """
    Shows the lessons of a course
    """
    print("\n=== Seleccionar lección ===")
    response = requests.get(f"{API_URL}/courses/{course_id}/lessons")

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: la respuesta de /courses/{course_id}/lessons no es JSON.")
        print(response.text)
        return None

    if not isinstance(data, list) or len(data) == 0:
        print("No hay lecciones para este curso.")
        return None

    # Mostrar lecciones numeradas
    for idx, lesson in enumerate(data, start=1):
        title = lesson.get("title", "sin título")
        order = lesson.get("order", "?")
        print(f"{idx}) [{order}] {title}")

    choice = input("Elige una lección por número: ")
    if not choice.isdigit():
        print("Opción no válida.")
        return None

    choice_idx = int(choice)
    if choice_idx < 1 or choice_idx > len(data):
        print("Número fuera de rango.")
        return None

    selected_lesson = data[choice_idx - 1]
    lesson_id = str(selected_lesson.get("_id") or selected_lesson.get("id"))
    if not lesson_id:
        print("No se encontró el ID de la lección.")
        return None

    return lesson_id

def complete_lesson_cli(current_user_email: str):
    """
    Marks a lesson as completed else not compelted
    """
    print("\n=== Marcar lección como completada ===")

    # 1) Seleccionar curso
    course_id = select_course_cli()
    if course_id is None:
        print("No se pudo seleccionar curso.")
        return

    # 2) Seleccionar lección
    lesson_id = select_lesson_cli(course_id)
    if lesson_id is None:
        print("No se pudo seleccionar lección.")
        return

    # 3) Estado
    status = input("Estado (entregada / no_entregada) [entregada]: ") or "entregada"

    payload = {
        "user_id": current_user_email,  # email como user_id
        "course_id": course_id,
        "lesson_id": lesson_id,
        "status": status,
    }

    response = requests.post(
        f"{API_URL}/progress/complete-lesson",
        json=payload
    )
    safe_print_response(response)

def my_progress_cli(current_user_email: str):
    """
    Seee the progress that a user has on a course
    """
    print("\n=== Ver mi progreso en un curso ===")

    course_id = select_course_cli()
    if course_id is None:
        print("No se pudo seleccionar curso.")
        return

    limit = input("¿Cuántos registros quieres ver? [10]: ") or "10"

    params = {
        "user_id": current_user_email,
        "limit": limit,
    }

    response = requests.get(
        f"{API_URL}/progress/my-progress/{course_id}",
        params=params
    )
    safe_print_response(response)


#=================================Courses and Lessons===================================================



# ---------- USERS ----------

def create_user_cli():
    """
    Can create a user
    """
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
    Log in function validator
    """
    print("\n=== Iniciar sesion ===")
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
        print("Error al iniciar sesion:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return None

    # Debe regresar: { "email": ..., "full_name": ..., "role": ... }
    print("\nLogin correcto. Usuario:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    return data


def update_user_cli(current_email: str) -> dict | None:
    """
    Updates the users either email or name or both
    """
    print("\n=== Actualizar usuario ===")
    print(f"Email actual: {current_email}")

    print("¿Que quieres actualizar?")
    print("1) Solo email")
    print("2) Solo nombre")
    print("3) Email y nombre")
    print("4) Cancelar")

    choice = input("Opcion: ")

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


# ---------- ADMIN (USUARIOS) ----------

def list_users_cli():
    print("\n=== Listar usuarios ===")
    response = requests.get(f"{API_URL}/users/")
    safe_print_response(response)

def update_user_role_cli(email,new_role):
    payload = {"role": new_role}
    response = requests.put(f"{API_URL}/users/{email}/role", json=payload)
    safe_print_response(response)

def delete_user_cli(email):
    payload = {"email": email}
    response=requests.delete(f"{API_URL}/users/{email}")
    safe_print_response(response)


