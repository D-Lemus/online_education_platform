# menu_admin.py
from Client_common import (
    list_users_cli,
    list_courses_cli,
    list_lessons_cli,
    update_user_cli,
    update_user_role_cli,
    delete_user_cli,
    update_course_cli,     # new: update a course
    update_lesson_cli,     # new: update a lesson
    delete_lesson_cli,     # new: delete a lesson
    delete_course_cli      # new: delete a course
)


def admin_menu(user_info: dict):
    """
    Admin menu.
    Admin can:
    - View all users
    - View all courses
    - View lessons of any course
    - Update own account
    - Update other users
    - Change user roles
    - Delete users
    - Update/Delete courses and lessons
    """
    while True:
        print(f"""
        === ADMIN MENU ===
        User: {user_info.get("full_name")} ({user_info.get("email")})
        Role: {user_info.get("role")}

        1) View all users
        2) View all courses
        3) View lessons of a course
        4) Update MY user (name)
        5) Update ANOTHER user by email
        6) Logout and return to main menu
        7) Update a user's role
        8) Delete a user
        9) Update a course
        10) Update a lesson
        11) Delete a lesson
        12) Delete a course
        """)

        option = input("Choose an option: ")

        if option == "1":
            list_users_cli()

        elif option == "2":
            list_courses_cli()

        elif option == "3":
            list_lessons_cli()

        elif option == "4":
            # Update own admin user (email/name)
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                # Sync local user info with new values
                user_info.update(updated)

        elif option == "5":
            # Update another user
            target_email = input("Email of user to update: ")
            update_user_cli(target_email)

        elif option == "6":
            print("Logging out (Admin)...")
            break

        elif option == "7":
            # Update user role
            target_email = input("Email of user: ")
            new_role = input("New role: ")
            update_user_role_cli(target_email, new_role)

        elif option == "8":
            # Delete a user
            target_email = input("Email of user to delete: ")
            delete_user_cli(target_email)

        elif option == "9":
            # Admin can update any course
            update_course_cli()

        elif option == "10":
            # Admin can update any lesson
            update_lesson_cli()

        elif option == "11":
            # Admin can delete any lesson
            delete_lesson_cli()

        elif option == "12":
            # Admin can delete any course
            delete_course_cli()

        else:
            print("Invalid option, please try again.")
