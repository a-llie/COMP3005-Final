

import psycopg2
from psycopg2 import sql
import os
from Trainer import Trainer
from Member import Member
from Admin import Admin
from System import System


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
    sessions = System.show_all_trainer_schedules(conn)
    member.browse_training_sessions(sessions, conn)

    session_choice = input(
        "Choose a session to book by entering the number: \n\n>>")
    session = sessions[int(session_choice) - 1]
    member.book_session(session, conn)


def menu(conn):
    while True:
        menu_choice = input(
            "Choose an option: \n 1. New User Registration \n 2. Club Member Sign In \n 3. Trainer Sign In  \n 4. Admin Sign in \n 5. Exit \n\n>>")
        match menu_choice:
            case "1":
                print("New User Registration")
                username = System.create_new_user(conn)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT c.first_name, c.last_name, c.user_weight FROM Club_Member c WHERE c.username = %s", [username])
                first_name, last_name, weight = cursor.fetchone()
                m = Member(username, first_name, last_name, weight, conn)
                m.options(conn)
            case "2":
                # temporary until sign in done
                user = input("Enter your username: ")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT c.username, c.first_name, c.last_name, c.user_weight FROM Club_Member c WHERE c.username = %s", [user])
                found = cursor.fetchone()
                if found is None:
                    print("User not found")
                    menu(conn)
                else:
                    user, first_name, last_name, weight = found
                    m = Member(user, first_name, last_name, weight, conn)
                    m.options(conn)
            case "3":
                # print("<insert trainer sign in here>")
                result = Trainer.sign_in(conn)
                if result is None:
                    print("User not found")
                    menu(conn)
                else:
                    id, first_name, last_name = result
                    t = Trainer(first_name, last_name, id, conn)
                    t.options()

            case "4":
                result = Admin.sign_in(conn)
                if result is None:
                    print("User not found")
                    menu(conn)
                else:
                    first_name, last_name = result
                    a = Admin(first_name, last_name, conn)
                    a.options()
            case "5":
                conn.close()
                exit()
            case _: 
                print("Invalid option")
                
                


if __name__ == "__main__":
    main()
