# menu_admin.py
from Client_common import (
    list_users_cli,
    list_courses_cli,
    list_lessons_cli,
    update_user_cli,
    update_user_role_cli,
    delete_user_cli
)



def admin_menu(user_info: dict):
    """
    Menu para usuarios con rol Admin.
    Más adelante puedes agregar:
    - Cambiar rol de usuarios
    - Eliminar usuarios
    - Ver logs de Cassandra, etc.
    """
    while True:
        print(f"""
=== MENÚ ADMIN ===
Usuario: {user_info.get("full_name")} ({user_info.get("email")})
Role: {user_info.get("role")}

1) Ver todos los usuarios
2) Ver todos los cursos
3) Ver lecciones de un curso
4) Actualizar MI usuario (email / nombre)
5) Actualizar OTRO usuario por email (admin)
6) Cerrar sesión y regresar al menú principal
7) Actualizar el rol un usuario
""")
        option = input("Elige una opción: ")

        if option == "1":
            list_users_cli()

        elif option == "2":
            list_courses_cli()

        elif option == "3":
            list_lessons_cli()

        elif option == "4":
            # Actualizar el propio usuario admin
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                user_info.update(updated)

        elif option == "5":
            # Admin actualiza a otro usuario
            target_email = input("Email del usuario a actualizar: ")
            update_user_cli(target_email)

        elif option == "6":
            print("Cerrando sesión de Admin...")
            break

        elif option == "7":
            # Admin actualiza a otro usuario
            target_email = input("Email del usuario a actualizar: ")
            new_role = input("Nuevo Rol: ")
            update_user_role_cli(target_email,new_role)

        elif option == "8":
            target_email = input("Email del usuario a eliminar: ")
            delete_user_cli(target_email)

        else:
            print("Opción no válida.")
