# menu_teacher.py
from Client_common import (
    list_courses_cli,
    create_course_cli,
    create_lesson_cli,
    list_lessons_cli,
    update_user_cli,
)


def teacher_menu(user_info: dict):
    """
    Menú para usuarios con rol Teacher.
    """
    while True:
        print(f"""
=== MENÚ TEACHER ===
Usuario: {user_info.get("full_name")} ({user_info.get("email")})
Role: {user_info.get("role")}

1) Crear curso
2) Crear lección para un curso
3) Ver todos los cursos
4) Ver lecciones de un curso
5) Actualizar mi perfil (email / nombre)
6) Cerrar sesión y regresar al menú principal
""")
        option = input("Elige una opción: ")

        if option == "1":
            create_course_cli()

        elif option == "2":
            create_lesson_cli()

        elif option == "3":
            list_courses_cli()

        elif option == "4":
            list_lessons_cli()

        elif option == "5":
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                user_info.update(updated)

        elif option == "6":
            print("Cerrando sesión de Teacher...")
            break

        else:
            print("Opción no válida.")
