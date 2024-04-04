import psycopg2

from Person import Person
from System import System


class Trainer(Person):

    trainer_ID: int

    def __init__(self, first_name, last_name, trainer_ID, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        self.trainer_ID = trainer_ID

    @staticmethod
    def sign_in(conn):
        id = input("Enter your id: ")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.employee_id, c.first_name, c.last_name FROM Employee c WHERE c.employee_id = %s AND c.is_trainer = TRUE", [id])
        found = cursor.fetchone()
        return found

    def options(self):
        while True:
            menu_choice = input(
                f'\n{self.first_name}, choose an option: \n 1. Schedule management \n 2. View member \n 3. See upcoming classes. \n 4. Sign Out \n\n>>')

            match menu_choice:
                case "1":
                    # manage the Schedule table(only refereing to the trianer singed in)
                    self.__manage_schedule_table()

                case "2":
                    while True:
                        choice = input(
                            "Would you like to search by: \n 1. username \n 2. name \n\n>>")
                        match choice:
                            case "1":
                                user = input("Input username: ")
                                out = System.get_member(user, self.conn)

                                if out is None:
                                    print("User not found")
                                    continue
                                elif len(out) > 1:
                                    i = 1
                                    print(
                                        "Multiple users found, enter number of user you'd like to see:")
                                    for user in out:
                                        print(f'{i}. {user[0]}')
                                        i += 1
                                    try:
                                        choice = int(input(">>"))
                                    except:
                                        print("Invalid choice")
                                        continue
                                else:
                                    choice = 1
                                print(out[choice - 1])
                                # display
                                System.print_member(out[choice - 1])

                                input("OK [Press Enter]")

                            case "2":
                                first = input("Input first name: ")
                                last = input("Input last name: ")
                                out = System.get_member(first, last, self.conn)
                                # display
                                System.print_member(out)

                                input("OK [Press Enter]")

                            case _:
                                print("Invalid option")

                case "3":
                    # see whats booked for you (in the class table )
                    self.__see_upcoming_classes()

                case "4":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")

    def __get_schedule(self):
        cursor = self.conn.cursor()

        # find all of trainer's schedule
        cursor.execute(
            'SELECT schedule_start, schedule_end FROM Schedule s  WHERE s.employee_id = %s AND s.schedule_start > current_timestamp', [self.trainer_ID])

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

    def __add_availability(self, start, end):  # psudo code
        # breack it into one our blocks
        duration = end - start  # might need a object/function for this
        cursor = self.conn.cursor()

        # insert adeal with round up to next hour here

        for i in range(duration):
            next_time = start + 1  # this may need a function too
            try:
                cursor.execute(
                    'INSERT INTO Schedule (employee_id, schedule_start, schedule_end) VALUES (%s, %s, %s)', [self.trainer_ID, start, next_time])

            except psycopg2.errors.UniqueViolation:
                pass

            start = next_time

    def __remove_availability(self, start, end):  # psudo code
        # breack it into one our blocks
        duration = end - start  # might need a object/function for this
        cursor = self.conn.cursor()

        # insert adeal with round up to next hour here

        for i in range(duration):
            next_time = start + 1  # this may need a function too
            try:
                cursor.execute(
                    'DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s AND schedule_end = %s', [self.trainer_ID, start, next_time])

            except psycopg2.errors.UniqueViolation:
                pass

            start = next_time

    def __manage_schedule_table(self):
        while True:
            menu_choice = input(
                'Would you like to: \n 1. Get schedule \n 2. Add availibility \n 3. Remove availability \n 4. Exit \n\n>>')

            match menu_choice:
                case "1":
                    self.__get_schedule()
                    input("OK [Press Enter]")
                    return
                case "2":
                    # take start time in format
                    start = input("Give Start time of block (in for ___): ")
                    # take end time in format
                    end = input("Give Start time of block (in for ___): ")

                    self.__add_availability(start, end)
                    input("OK [Press Enter]")
                    return
                case "3":
                    # take start time in format
                    start = input(
                        "Give Start time of block you would like to remvoe (in for ___):\n ")
                    end = input(
                        "Give end time of block you would like to remvoe (in for ___):\n ")

                    self.__remove_availability(start, end)
                    input("OK [Press Enter]")
                    return
                case "4":
                    break
                case _:
                    print("Invalid option")
                    return

    def __see_upcoming_classes(self):
        cursor = self.conn.cursor()

        # find all classes that user is registered in
        cursor.execute(
            'SELECT c.class_time, c.room_num, c.exercise_type, c.registered FROM Class c WHERE c.trainer_id = %s AND c.class_time > current_timestamp', [self.trainer_ID])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.")
            return

        print("Upcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Exercise Type".ljust(25)} | {"# Registered".ljust(5)} ')
        print('-' * 95)
        for row in results:
            print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {row[2].ljust(25)} | {str(row[3]).ljust(5)}')

        print('-' * 95)
