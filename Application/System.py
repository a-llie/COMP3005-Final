import psycopg2

# placeholder

MAINTANANCE_INTERVAL = 3  # months


class System():

    def add_class(room, start_time, trainer_id, capacity, exercise="", registered=0):
        pass

    def get_free_room():
        pass

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
