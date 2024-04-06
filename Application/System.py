import psycopg2
from multipledispatch import dispatch
from datetime import datetime, timedelta
# placeholder

MAINTANANCE_INTERVAL = 3  # months


class System():
    @staticmethod
    def prompt_for_number(prompt: str):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("\nInvalid input.\n")

    @staticmethod
    def add_class(conn, room_id, start, trainer_id, capacity, registered, exercise, price):
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Class (room_num, class_time, trainer_id, capacity, registered, exercise_type,price) VALUES (%s, %s, %s, %s, %s, %s, %s)', [room_id, start, trainer_id, capacity, registered, exercise, price])
        conn.commit()

        cursor.execute(
            'SELECT class_id FROM Class WHERE room_num = %s AND class_time = %s', [room_id, start])

        exer_class = cursor.fetchone()

        print(f"Class {exer_class[0]} added successfully.")

    @staticmethod
    def get_free_room(conn, time):
        cursor = conn.cursor()
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        for i in range(num_rooms):
            cursor.execute(
                'SELECT c.room_num FROM Class c WHERE c.room_num = %s AND c.class_time = %s', [i, time])
            if not cursor.fetchone():
                return i

    @staticmethod
    def show_all_trainer_schedules(conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, schedule_start FROM Schedule ORDER BY schedule_start")
        return cursor.fetchall()

    @staticmethod
    def create_new_user(conn):
        username = input("Enter a username: ")

        while True:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM Club_Member WHERE username = %s", [username])
            if cursor.fetchone():
                print("\nUsername already exists.\n")
                username = input("Enter a username: ")
            else:
                break

        first_name = input("Enter your first name: ")
        while not first_name:
            first_name = input("Enter your first name: ")

        last_name = input("Enter your last name: ")
        while not last_name:
            last_name = input("Enter your last name: ")

        weight = System.prompt_for_number("Enter your weight: ")
        weight_goal = System.prompt_for_number("Enter your weight goal: ")
        height = System.prompt_for_number("Enter your height: ")

        membership_type = None
        while True:
            membership_type = System.prompt_for_number(
                "Enter your membership type: 1. Basic, 50$/month, 2. Pro, 75$/month: ")
            if membership_type not in [1, 2]:
                print("Invalid membership type\n")
                continue
            break
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Club_Member (username, first_name, last_name, user_weight, height, weight_goal, membership_type, join_date) VALUES (%s, %s, %s, %s, %s, %s, %s,NOW())', [username, first_name, last_name, weight, height, weight_goal, membership_type])

        membership_fee = 50.00 if membership_type == 1 else 75.00
        cursor.execute(
            'INSERT INTO Invoice(username, invoice_date, amount, invoiced_service, paid) VALUES (%s, NOW(), %s, %s, %s)', [username, membership_fee, 'Membership Fee', 'false'])

        print(f"\nUser {username} created successfully.\n")
        conn.commit()

        return username

    @staticmethod
    @dispatch(str, psycopg2.extensions.connection)
    def get_member(username, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, monthly_free, membership_type, first_name, last_name, user_weight, height, weight_goal  FROM Club_Member  WHERE username LIKE %s", ['%' + username + '%'])
        return cursor.fetchall()

    @staticmethod
    @dispatch(str, str, psycopg2.extensions.connection)
    def get_member(first, last, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, monthly_free, membership_type, first_name, last_name, user_weight, height, weight_goal  FROM Club_Member  WHERE first_name LIKE %s AND last_name LIKE %s", [first, last])
        return cursor.fetchall()

    @staticmethod
    def print_member(list: tuple):
        if list is None:
            return
        # username, monthly_free, membership_type, first_name, last_name, user_weight, height, weight_goal
        print(f'User info for {list[0]}:')
        membership = "Basic" if list[2] == 0 else "Pro"
        print(f'#username: {list[0]}, \nmonthly_free: {list[1]}, \nmembership_type: {membership}, \nfirst_name: {list[3]}, \nlast_name: {list[4]}, \nuser_weight: {list[5]}, \nheight: {list[6]}, \nweight_goal: {list[7]}')

    @staticmethod
    def get_trainer_schedule(conn, trainer_id):
        cursor = conn.cursor()

        # find all of trainer's schedule
        cursor.execute(
            'SELECT schedule_start, schedule_end FROM Schedule s  WHERE s.employee_id = %s AND s.schedule_start > current_timestamp ORDER BY schedule_start ASC', [trainer_id])

        results = cursor.fetchall()
        if not results:
            print("Nothing Scheduled.")
            return

        print(f'{" Start Time".ljust(20)} | {"End time".ljust(20)} ')
        print('-' * 50)
        for row in results:
            print(
                f' {str(row[0]).ljust(20)} | {str(row[1]).ljust(20)} ')

        print('-' * 50)

    @staticmethod
    def get_class_schedule(conn):
        cursor = conn.cursor()

        cursor.execute(
            'SELECT c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity FROM Class c AND c.class_time > current_timestamp')

        results = cursor.fetchall()
        if not results:
            print("Nothing Scheduled.")
            return

        print("Upcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Exercise Type".ljust(20)} | {"Registered".ljust(5)} | {"Capacity".ljust(5)} ')
        print('-' * 95)
        for row in results:
            print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {row[3].ljust(20)} | {row[4].ljust(5)} | {row[5].ljust(5)}')

        print('-' * 95)
