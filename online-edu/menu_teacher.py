# menu_teacher.py

from Client_common import (
    list_my_courses_cli,
    create_course_cli,
    create_lesson_cli,
    list_lessons_cli,
    update_user_cli,
    list_students_in_course_cli,
    unenroll_student_from_course_cli,
    update_course_cli,
    update_lesson_cli,
    delete_lesson_cli,
    delete_course_cli
)


def teacher_menu(user_info: dict):
    """
    Menu for users with role Teacher.
    Teachers can only modify or delete THEIR own courses.
    """
    while True:
        print(f"""
    === TEACHER MENU ===
    User: {user_info.get("full_name")} ({user_info.get("email")})
    Role: {user_info.get("role")}

    1) Create course
    2) Create lesson for one of my courses
    3) View my courses
    4) View lessons of one of my courses
    5) View students enrolled in one of my courses
    6) Unenroll a student from one of my courses
    7) Update my profile (name)
    8) Update one of my courses
    9) Update a lesson in one of my courses
    10) Delete a lesson in one of my courses
    11) Delete one of my courses
    12) Logout and return to main menu
    """)

        option = input("Choose an option: ")

        if option == "1":
            create_course_cli(user_info["email"])

        elif option == "2":
            create_lesson_cli()

        elif option == "3":
            list_lessons_cli(user_info["email"], only_my_courses=True)

        elif option == "4":
            list_lessons_cli(user_info["email"])

        elif option == "5":
            list_students_in_course_cli(user_info["email"])

        elif option == "6":
            unenroll_student_from_course_cli(user_info["email"])

        elif option == "7":
            updated = update_user_cli(user_info["email"])
            if updated is not None:
                user_info.update(updated)

        elif option == "8":
            update_course_cli(user_info["email"], only_my_courses=True)

        elif option == "9":
            update_lesson_cli(user_info["email"], only_my_courses=True)

        elif option == "10":
            delete_lesson_cli(user_info["email"], only_my_courses=True)

        elif option == "11":
            # Delete one of the teacher's own courses
            delete_course_cli(user_info["email"], only_my_courses=True)

        elif option == "12":
            print("Logging out (Teacher)...")
            break

        else:
            print("Invalid option.")
