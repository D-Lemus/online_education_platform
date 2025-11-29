# menu_student.py
from Client_common import (
    list_courses_cli,
    list_lessons_cli,
    update_user_cli,
)


def student_menu(user_info: dict):
    """
    Menú para usuarios con rol Student.
    user_info: dict con email, full_name, role.
    """
    while True:
        print(f"""
=== MENÚ STUDENT ===
Usuario: {user_info.get("full_name")} ({user_info.get("email")})
Role: {user_info.get("role")}

1) Ver todos los cursos
2) Ver lecciones de un curso
3) Actualizar mi perfil (email / nombre)
4) Cerrar sesión y regresar al menú principal
""")
        option = input("Elige una opción: ")

        if option == "1":
            list_courses_cli()

        elif option == "2":
            list_lessons_cli()

        elif option == "3":
            # Actualizamos usando el email actual
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                # Actualizamos también la info local para que el menú muestre los nuevos datos
                user_info.update(updated)

        elif option == "4":
            print("Cerrando sesión de Student...")
            break

        else:
            print("Opción no válida.")
