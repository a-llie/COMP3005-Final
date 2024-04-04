import psycopg2
from multipledispatch import dispatch
# placeholder

MAINTANANCE_INTERVAL = 3  # months


class System():

    @staticmethod
    def add_class(conn, room_id, start, trainer_id, capacity, registered, exercise):
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Class (room_num, class_time, trainer_id, capacity, registered, exercise_type) VALUES (%s, %s, %s, %s, %s, %s)', [room_id, start, trainer_id, capacity, registered, exercise])
        conn.commit()

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
        first_name = input("Enter your first name: ")
        last_name = input("Enter your last name: ")

        try:
            weight = int(input("Enter your weight: "))
        except ValueError:
            print("Invalid weight")
            return

        try:
            height = int(input("Enter your height: "))
        except ValueError:
            print("Invalid height")
            return

        try:
            weight_goal = input("Enter your weight goal: ")
        except ValueError:
            print("Invalid weight goal")
            return

        try:
            membership_type = int(
                input("Enter your membership type: 1. Basic, 50$/month, 2. Pro, 75$/month"))
        except ValueError:
            print("Invalid membership type")
            return

        if membership_type not in [1, 2]:
            print("Invalid membership type")
            return

        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO Club_Member (username, first_name, last_name, user_weight, height, weight_goal, membership_type) VALUES (%s, %s, %s, %s, %s, %s, %s)', [username, first_name, last_name, weight, height, weight_goal, membership_type])
        except psycopg2.errors.UniqueViolation:
            print("Username already exists")
            return

        print("User created successfully.")
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
        # username, monthly_free, membership_type, first_name, last_name, user_weight, height, weight_goal
        print(f'User info for {list[0]}:')
        membership = "Basic" if list[2] == 0 else "Pro"
        print(f'#username: {list[0]}, \nmonthly_free: {list[1]}, \nmembership_type: {membership}, \nfirst_name: {list[3]}, \nlast_name: {list[4]}, \nuser_weight: {list[5]}, \nheight: {list[6]}, \nweight_goal: {list[7]}')
