

import psycopg2
from psycopg2 import sql
import os
from Trainer import Trainer
from Member import Member
from Admin import Admin
from System import System
from gym_utils import Utils

DB_NAME = 'Gym'
HOST = 'localhost'
PORT = '5432'


def main():
    user = os.environ['POSTGRES_USER']
    password = os.environ['POSTGRES_PASS']

    conn = psycopg2.connect(dbname=DB_NAME, user=user,
                            password=password, host=HOST, port=PORT)
    menu(conn)


# temporary until sign in done
def member_book_session(conn, member: Member):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT c.user_weight FROM Club_Member c WHERE c.username = %s", [member.username])
    sessions = System.get_all_trainer_schedules(conn)
    member.browse_training_sessions(sessions, conn)

    session_choice = input(
        "Choose a session to book by entering the number: \n\n>>")
    session = sessions[int(session_choice) - 1]
    member.book_session(session, conn)


def menu(conn):
    options = [
        "New User Registration",
        "Club Member Sign In",
        "Trainer Sign In",
        "Admin Sign in",
        "Exit",
        "DEBUG FUNCTIONS"
    ]

    menu_options = ""
    for i, option in enumerate(options):
        menu_options += f"{i+1}. {option}\n"

    while True:
        menu_choice = input(
            f"Choose an option: \n{menu_options}\n>>")
        match menu_choice:
            case "1":
                Utils.print_menu_header(options[0])
                username = System.create_new_user(conn)
                m = Member.sign_in(conn, username)
                m.options()
            case "2":
                Utils.print_menu_header(options[1])
                m = Member.sign_in(conn)
                if m is not None:
                    m.options()
            case "3":
                Utils.print_menu_header(options[2])
                while True:
                    result = Trainer.sign_in(conn)
                    if result is None:
                        print("Trainer ID not found.\n")
                    else:
                        break
                id, first_name, last_name = result
                t = Trainer(first_name, last_name, id, conn)
                t.options()
            case "4":
                Utils.print_menu_header(options[3])
                while True:
                    result = Admin.sign_in(conn)
                    if result is None:
                        print("Admin ID not found.\n")
                    else:
                        break
                first_name, last_name = result
                a = Admin(first_name, last_name, conn)
                a.options()
            case "5":
                print("Exiting...")
                conn.close()
                exit()
            case "6":
                debug_menu(conn)
            case _:
                print("Invalid option.\n")


def debug_menu(conn):
    tables = [
        "Employee",
        "Club_Member",
        "Equipment",
        "Class",
        "Schedule",
        "Invoice",
        "Exercise"
    ]

    options = ""
    for i, table in enumerate(tables):
        options += f"{i+1}. {table}\n"
    while True:
        menu_choice = int(input(
            f"Choose an option: \n {options} \n{len(tables)+1} Back. \n\n>>"))
        if menu_choice >= 0 and menu_choice <= len(tables):
            table = tables[menu_choice-1]
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        elif menu_choice == len(tables)+1:
            menu(conn)
        else:
            print("Invalid option.\n")


if __name__ == "__main__":
    main()
