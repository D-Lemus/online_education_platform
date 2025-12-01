from Client_common import (
    list_courses_cli,
    list_lessons_cli,
    update_user_cli,
    enroll_in_course_cli,
    list_my_enrolled_courses_cli,
)
def student_menu(user_info: dict):
    """
    Menu for users with role Student.
    """
    while True:
        print(f"""
=== STUDENT MENU ===
User: {user_info.get("full_name")} ({user_info.get("email")})
Role: {user_info.get("role")}

1) View all available courses
2) View my enrolled courses
3) Enroll in a course
4) View lessons of a course 
5) Update my profile (name)
6) Logout and return to main menu
""")
        option = input("Choose an option: ")

        if option == "1":
            # All courses from Mongo (no filter)
            list_courses_cli()

        elif option == "2":
            # Only courses where this student is enrolled (Dgraph + Mongo)
            list_my_enrolled_courses_cli(user_info["email"])

        elif option == "3":
            # Enroll current student in a course (Dgraph)
            enroll_in_course_cli(user_info["email"])

        elif option == "4":
            # For now, reuse the generic lessons listing
            list_lessons_cli()

        elif option == "5":
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                user_info.update(updated)

        elif option == "6":
            print("Logging out (Student)...")
            break

        else:
            print("Invalid option.")
