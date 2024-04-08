import psycopg2
from multipledispatch import dispatch
from datetime import datetime, timedelta
from gym_utils import Utils
# placeholder

MAINTANANCE_INTERVAL = 3  # months


class System():
    @staticmethod
    def add_class(conn, room_id, start, trainer_id, capacity, registered, exercise, price):
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO Class (room_num, class_time, trainer_id, capacity, registered, exercise_type, price) VALUES (%s, %s, %s, %s, %s, %s, %s)', [room_id, start, trainer_id, capacity, registered, exercise, price])
            conn.commit()
        except psycopg2.errors.NotNullViolation as e:
            print("ERROR: class insert error:\n%s", [e])
            print("Invalid time, please try again")
            return

        cursor.execute(
            'SELECT  c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity, c.price  FROM Class c WHERE c.room_num = %s AND c.class_time = %s', [room_id, start])

        exer_class = cursor.fetchone()

        print(f"\nClass {str(exer_class[0])} added successfully.\n")
        Utils.print_table(
            [("Class Time", 20), ("Room Number", 15), ("Trainer ID", 15), ("Exercise Type", 20), ("Registered", 10), ("Capacity", 10), ("Price", 10)], [exer_class], [20, 15, 15, 20, 10, 10, 10])

        Utils.OK()

    @staticmethod
    def get_free_room(conn, time):
        cursor = conn.cursor()
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        i = 1

        for i in range(num_rooms):
            cursor.execute(
                'SELECT c.room_num FROM Class c WHERE c.room_num = %s AND c.class_time = %s LIMIT 1', [i, time])
            result = cursor.fetchone()
            if result is None:
                return i

        return None

    @staticmethod
    def get_all_trainer_schedules(conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT employee_id, schedule_start FROM Schedule ORDER BY schedule_start")
        return cursor.fetchall()

    @staticmethod
    def get_all_available_classes(conn, username=None):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT class_time, capacity, registered, exercise_type, price, trainer_id, class_id FROM Class c WHERE class_time > NOW() AND capacity > registered AND not exists (SELECT * FROM Exercise e WHERE e.username = %s AND e.class_id = c.class_id) ORDER BY class_time", [username])
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

        weight = Utils.prompt_for_number("Enter your weight: ")
        weight_goal = Utils.prompt_for_number("Enter your weight goal: ")
        #height = Utils.prompt_for_number("Enter your height: ")
        cardio_time = Utils.prompt_for_number(
            "How long can you currently do cardio for? (in minutes): ")
        lifting_weight = Utils.prompt_for_number(
            "How much can you currently lift? (in lbs): ")

        membership_type = None
        while True:
            membership_type = Utils.prompt_for_number(
                "Enter your membership type: 1. Basic, 50$/month, 2. Pro, 75$/month: ")
            if membership_type not in [1, 2]:
                print("Invalid membership type\n")
                continue
            break
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Club_Member (username, first_name, last_name, membership_type, join_date) VALUES (%s, %s, %s, %s, NOW())', [username, first_name, last_name, membership_type])

        cursor.execute(
            'INSERT INTO Health (username, date, weight, cardio_time, lifting_weight, weight_goal) VALUES (%s, NOW(), %s, %s, %s, %s)', [username, weight, cardio_time, lifting_weight, weight_goal])
        print(f"\nUser {username} created successfully.\n")
        conn.commit()

        return username

    @staticmethod
    @dispatch(str, psycopg2.extensions.connection)
    def find_members(username, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, monthly_fee, membership_type, first_name, last_name FROM Club_Member  WHERE username LIKE %s", ['%' + username + '%'])
        return cursor.fetchall()

    @staticmethod
    @dispatch(str, str, psycopg2.extensions.connection)
    def find_members(first, last, conn):
        cursor = conn.cursor()
        if first == "" and last == "":
            cursor.execute(
                "SELECT username, monthly_fee, membership_type, first_name, last_name FROM Club_Member")
            return cursor.fetchall()
        if first == "":
            cursor.execute(
                "SELECT username, monthly_fee, membership_type, first_name, last_name  FROM Club_Member  WHERE last_name ILIKE %s", [last])
            return cursor.fetchall()
        if last == "":
            cursor.execute(
                "SELECT username, monthly_fee, membership_type, first_name, last_name  FROM Club_Member  WHERE first_name ILIKE %s", [first])
            return cursor.fetchall()

    @staticmethod
    def print_member(user):
        if user == [] or user is None:
            return
        # username, monthly_free, membership_type, first_name, last_name,
        print(f'User info for {user[0]}:')
        membership = "Basic" if user[2] == 0 else "Pro"

        user = list(user)
        user[2] = membership

        Utils.print_table(
            [("Username", max(len(user[0]), len("Username"))), ("Monthly Fee", 15), ("Membership Type", 15), ("First Name", max(len(user[3]), len("First Name"))), ("Last Name", max(len(user[4]), len("Last Name")))]
            , [user],
              [max(len(user[0]), len("Username")), 15, 15, max(len(user[3]), len("First Name")), max(len(user[4]), len("Last Name"))], False)

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
            'SELECT c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity FROM Class c AND c.class_time > current_timestamp ORDER BY c.class_time ASC')

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

    @staticmethod
    def create_class_invoice(conn, username, class_id):
        cursor = conn.cursor()
        cursor.execute(
            'SELECT price FROM Class WHERE class_id = %s', [class_id])
        price = cursor.fetchone()[0]

        cursor.execute(
            'INSERT INTO Invoice (username, amount, invoice_date, invoiced_service, paid) VALUES (%s, %s, NOW(), %s, false)', [username, price, class_id])

        print(f"Invoice for class {class_id} created successfully.")
