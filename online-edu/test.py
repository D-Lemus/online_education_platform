import requests
import json

API_URL = "http://127.0.0.1:8001"


def safe_print_response(response):
    """Imprime la respuesta sin crashear cuando no es JSON."""
    print("Status code:", response.status_code)

    try:
        data = response.json()
        print("JSON:", data)
    except json.JSONDecodeError:
        print("El servidor no devolvió JSON. Cuerpo bruto:")
        print(response.text)


def create_user():
    print("\n=== Crear Usuario ===")
    email = input("Email: ")
    full_name = input("Nombre completo: ")
    password = input("Contraseña: ")
    role = input("Rol (Student/Teacher): ") or "Student"

    payload = {
        "email": email,
        "full_name": full_name,
        "password": password,
        "role": role
    }

    response = requests.post(f"{API_URL}/users/", json=payload)
    safe_print_response(response)


def create_course():
    print("\n=== Crear Curso ===")
    course_name = input("Nombre del curso: ")
    taught_by = input("Profesor: ")

    payload = {
        "course_name": course_name,
        "taught_by": taught_by
    }

    response = requests.post(f"{API_URL}/courses/", json=payload)
    safe_print_response(response)


def create_lesson():
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


def main():
    while True:
        print("""
=== MENU ===
1) Crear usuario
2) Crear curso
3) Crear lección
4) Salir
""")
        choice = input("Opción: ")

        if choice == "1":
            create_user()
        elif choice == "2":
            create_course()
        elif choice == "3":
            create_lesson()
        elif choice == "4":
            print("Bye!")
            break
        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main()
