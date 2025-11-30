from Client_common import (
    list_courses_cli,
    list_lessons_cli,
    update_user_cli,
    complete_lesson_cli,
    my_progress_cli,
)

def student_menu(user_info: dict):
    while True:
        print(f"""
=== MENÚ STUDENT ===
Usuario: {user_info.get("full_name")} ({user_info.get("email")})
Role: {user_info.get("role")}

1) Ver todos los cursos
2) Ver lecciones de un curso
3) Marcar lección como completada
4) Ver mi progreso en un curso
5) Actualizar mi perfil (email / nombre)
6) Cerrar sesión y regresar al menú principal
""")
        option = input("Elige una opción: ")

        if option == "1":
            list_courses_cli()

        elif option == "2":
            # aquí puedes usar select_course_cli y no filtrar por inscripción todavía
            list_lessons_cli(None)  # puedes adaptar la función para aceptar None

        elif option == "3":
            complete_lesson_cli(user_info["email"])

        elif option == "4":
            my_progress_cli(user_info["email"])

        elif option == "5":
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                user_info.update(updated)

        elif option == "6":
            print("Cerrando sesión de Student.")
            break

        else:
            print("Opción no válida.")
