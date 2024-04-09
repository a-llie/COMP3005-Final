
from psycopg2 import sql
import os
from Trainer import Trainer
from Member import Member
from Admin import Admin
from System import System
from gym_utils import Utils


def main():
    conn = System.create_connection()
    menu(conn)


def menu(conn):
    options = [
        "New User Registration",
        "Club Member Sign In",
        "Trainer Sign In",
        "Admin Sign in",
        "Exit",
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
            case _:
                print("Invalid option.\n")


if __name__ == "__main__":
    main()
