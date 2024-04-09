import psycopg2
import math

from Person import Person
from System import System
from gym_utils import Utils


class Trainer(Person):

    trainer_ID: int

    def __init__(self, first_name, last_name, trainer_ID, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        self.trainer_ID = trainer_ID

    @staticmethod
    def sign_in(conn):
        id = Utils.prompt_for_number("Enter your employee ID: ")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.employee_id, c.first_name, c.last_name FROM Employee c WHERE c.employee_id = %s AND c.is_trainer = TRUE", [id])
        found = cursor.fetchone()
        return found

    def options(self):
        while True:
            Utils.print_menu_header("Trainer Menu")
            menu_choice = input(
                f'\n{self.first_name}, choose an option: \n 1. Schedule management \n 2. View member \n 3. See upcoming classes. \n 4. Sign Out \n\n>>')

            match menu_choice:
                case "1":
                    # manage the Schedule table(only refereing to the trianer singed in)
                    self.__manage_schedule_table()

                case "2":
                    self.search_for_member()
                    Utils.OK()

                case "3":
                    # see whats booked for you (in the class table )
                    self.__see_upcoming_classes()
                    Utils.OK()
                case "4":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option.\n")

    def __add_availability(self, start, dur: int):  # psudo code
        # breack it into one hour blocks
        cursor = self.conn.cursor()
        error = False
        success_count = 0

        for i in range(dur):
            next_time = Utils.datetime_add_hour(start)
            try:
                cursor.execute(
                    'INSERT INTO Schedule (employee_id, schedule_start, schedule_end) VALUES (%s, %s, %s)', [self.trainer_ID, start, next_time])
                self.conn.commit()
                success_count += 1
            except psycopg2.errors.UniqueViolation as e:
                print(
                    f"ERROR: Failed to add availability {start}. ")
                self.conn, cursor = System.reset_connection(self.conn)
                error = True
            start = next_time

        if not error:
            print("Availability added successfully.")
        if error and success_count > 0:
            print("Some availability added successfully.")
        if error and success_count == 0:
            print("No availability added successfully.")
        else:
            print("All availability added successfully.")

    def __remove_availability(self, start, dur: int):  # psudo code
        # breack it into one our blocks

        cursor = self.conn.cursor()
        error = False
        success_count = 0

        for i in range(dur):
            next_time = Utils.datetime_add_hour(start)
            try:
                cursor.execute(
                    'DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s AND schedule_end = %s', [self.trainer_ID, start, next_time])
                self.conn.commit()
                success_count += 1
            except psycopg2.errors.UniqueViolation as e:
                print(
                    f"ERROR: Failed to remove availability {start}.")

                self.conn, cursor = System.reset_connection(self.conn)
                error = True

            start = next_time

        if not error:
            print("Availability removed successfully.")
        if error and success_count > 0:
            print("Some availability removed successfully.")
        else:
            print("All availability removed successfully.")

    def __manage_schedule_table(self):
        while True:
            menu_choice = input(
                'Would you like to: \n 1. Get schedule \n 2. Add availibility \n 3. Remove availability \n 4. Exit \n\n>>')

            match menu_choice:
                case "1":
                    System.get_trainer_schedule(self.conn, self.trainer_ID)
                    Utils.OK()

                case "2":
                    # take start time in format
                    start = Utils.get_datetime(
                        "Specify your availability: \n", False)
                    # take end time in format
                    dur = Utils.prompt_for_number(
                        "How many hours will you be working for? \n>> ")

                    self.__add_availability(start, dur)

                    Utils.OK()

                case "3":

                    schedule = System.get_trainer_schedule(
                        self.conn, self.trainer_ID, False)

                    if schedule is None:
                        print("No schedule found.")
                        continue

                    print("Your schedule:")
                    Utils.print_table(
                        [("Start Time", 20), ("End Time", 20)], schedule, [20, 20], True)

                    while True:
                        choice = Utils.prompt_for_number(
                            "Choose a block to remove from the numbered options above: \n>> ")

                        if choice < 1 or choice > len(schedule):
                            print("Invalid choice.")
                            continue
                        break

                    start = schedule[choice - 1][0]

                    continuous = Utils.prompt_for_non_blank(
                        "Would you like to remove a consecutive number of hours? [y/n] \n>> ")

                    if continuous.lower() == "y":
                        dur = Utils.prompt_for_number(
                            "How many hours will you be removing: \n>> ")
                    else:
                        dur = 1

                    self.__remove_availability(start, dur)
                    Utils.OK()

                case "4":
                    break
                case _:
                    print("Invalid option.\n")

    def __see_upcoming_classes(self):
        cursor = self.conn.cursor()

        # find all classes that user is registered in
        cursor.execute(
            'SELECT c.class_time, c.room_num, c.exercise_type, c.registered FROM Class c WHERE c.trainer_id = %s AND c.class_time > current_timestamp ORDER BY c.class_time ASC', [self.trainer_ID])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.")
            return

        Utils.print_menu_header("Your Upcoming Classes")

        Utils.print_table(
            [("Class Time", 20), ("Room Number", 15), ("Exercise Type", 25), ("# Registered", 12)], results, [20, 15, 25, 12], False)
