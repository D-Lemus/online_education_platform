# menu_main.py
from Client_common import create_user_cli, login_cli
import menu_student
import menu_teacher
import menu_admin


def main_menu():
    while True:
        print("""
=== MENÚ PRINCIPAL ===
1) Registrarse (crear usuario)
2) Iniciar sesión
3) Salir
""")
        option = input("Elige una opción: ")

        if option == "1":
            create_user_cli()

        elif option == "2":
            user = login_cli()
            if user is None:
                # login fallido, regresamos al menú
                continue

            role = user.get("role", "Student")
            print(f"\nRol detectado: {role}")

            if role == "Student":
                menu_student.student_menu(user)
            elif role == "Teacher":
                menu_teacher.teacher_menu(user)
            elif role == "Admin":
                menu_admin.admin_menu(user)
            else:
                print("Rol desconocido, regresando al menú principal.")

        elif option == "3":
            print("Adiós")
            break

        else:
            print("Opción no válida.")


if __name__ == "__main__":
    main_menu()
