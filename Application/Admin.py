

from Person import Person
from System import System
from gym_utils import Utils


class Admin(Person):

    def __init__(self, first_name, last_name, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        return

    @staticmethod
    def sign_in(conn):
        id = input("Enter your id: ")
        print("\n")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.first_name, c.last_name FROM Employee c WHERE c.employee_id = %s AND c.is_trainer = FALSE", [id])
        found = cursor.fetchone()
        return found

    def options(self):
        while True:
            menu_choice = input(
                f'choose an option: \n 1. View member \n 2. Manage Rooms. \n 3. Manage Equipment \n 4. Manage Upcoming Classes \n 5. Manage Billing \n 6. Sign Out \n\n>>')

            match menu_choice:

                case "1":
                    choice = input(
                        "Would you like to search by: \n 1. username \n 2. name \n")
                    match choice:
                        case "1":
                            user = input("Input username: ")
                            out = System.get_member(user, self.conn)
                            # dispaly
                            print(out)

                            if out == [] or out is None:
                                print("Not Found\n")
                                continue
                            System.print_member(out)

                            input("")
                            continue

                        case "2":
                            first = input("Input first name: ")
                            last = input("Input last name: ")
                            out = System.get_member(first, last, self.conn)
                            # dispaly
                            if out == [] or out is None:
                                print("Not Found\n")
                                continue
                            System.print_member(out)

                            input("")
                            continue

                        case _:
                            print("Invalid option")
                            print("")

                case "2":
                    # add a ability to toggle a romm so that it cant be booked?
                    self.__view_rooms()
                    input("")

                case "3":
                    choice = input(
                        "Would you like to: \n 1. View Equipment \n 2. Service Equipment\n")
                    match choice:
                        case "1":

                            self.__get_all_equipment()
                            input("")
                            continue

                        case "2":
                            id = input("Input equipment ID: ")

                            self.__maintain_equipment(id)
                            continue

                        case _:
                            print("Invalid option")

                case "4":
                    choice = input(
                        "Would you like to: \n 1. View Upcoming Classes \n 2. Add a Class \n 3. Remove a Class(by time and trainer) \n 4. Remove a Class(by class id)\n")
                    match choice:
                        case "1":

                            self.__get_class_schedule()
                            input("")
                            continue

                        case "2":

                            while True:
                                trainer = Utils.prompt_for_number(
                                    "ID of trainer who will teach the class: ")
                                cursor = self.conn.cursor()
                                cursor.execute(
                                    'SELECT employee_id, first_name FROM Employee WHERE employee_id = %s AND is_trainer = true', [trainer])
                                result = cursor.fetchone()
                                if not result:
                                    print("Trainer not found.")
                                    continue
                                break
                            name = result[1]
                            time = input(
                                "When will the class be (YYYY-MM-DD HH:MM): ")
                            exercise = input(
                                f"What will {name} be teaching: ")

                            cap = Utils.prompt_for_number(
                                "What is the capacity: ")
                            price = Utils.prompt_for_number(
                                "What is the price: ")

                            self.__add_class(
                                trainer, time, exercise, price, cap)
                            continue

                        case "3":
                            time = input("When dose the class start: ")
                            trainer = input("Who is teaching the class: ")
                            self.__remove_class(time, trainer)

                        case "4":
                            class_id = input("What is the class ID: ")
                            self.__remove_class(class_id)

                        case _:
                            print("Invalid option")

                case "5":
                    self.__bill_all()
                case "6":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")

    def __get_class_schedule(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity FROM Class c WHERE c.class_time > current_timestamp ORDER BY class_time')

        results = cursor.fetchall()
        if not results:
            print("Nothing Scheduled.")
            return

        print("Upcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Trainer ID".ljust(20)} | {"Exercise Type".ljust(20)} | {"Registered".ljust(10)} | {"Capacity".ljust(10)} ')
        print('-' * 95)
        for row in results:
            #print(row)
            print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {str(row[2]).ljust(20)} | {str(row[3]).ljust(20)} | {str(row[4]).ljust(10)} | {str(row[5]).ljust(10)}')

        print('-' * 95)

    def __add_class(self, trainer_id, start, exercise, price, capacity=5):
        cursor = self.conn.cursor()

        # remove that block from the free scedual of the trainer
        cursor.execute('DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s', [
                       trainer_id, start])
        self.conn.commit()

        # pick a free room (in system.py)
        room_id = System.get_free_room(self.conn, start)
        # creat class
        System.add_class(self.conn, room_id, start, trainer_id, capacity, 0, exercise, price)

    def __remove_class(self, start, id):
        cursor = self.conn.cursor()

        # romovce all exercises that have the class as a foren key
        # get the class id
        cursor.execute(
            'SELECT class_id FROM Class WHERE class_time = %s AND trainer_id = %s', [start, id])
        class_id = cursor.fetchone()[0]

        cursor.execute('DELETE FROM Exercise WHERE class_id = %s', [class_id])
        self.conn.commit()

        # remove the class
        cursor.execute(
            'DELETE FROM Class WHERE class_time = %s AND trainer_id = %s', [start, id])
        self.conn.commit()

    def __remove_class(self, class_id):
        cursor = self.conn.cursor()

        # romovce all exercises that have the class as a foren key
        cursor.execute('DELETE FROM Exercise WHERE class_id = %s', [class_id])
        self.conn.commit()

        # remove the class
        cursor.execute('DELETE FROM Class WHERE class_id = %s', [class_id])
        self.conn.commit()

    def __view_rooms(self):
        # view what rooms were booked and by what classes
        # search class and take the room and class, but also lifst rooms that arn't booked
        cursor = self.conn.cursor()
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        # header
        print("Rooms in Building 1:")  # CURRENTLY HARD CODDED
        print(f'     {"Room Number".ljust(20)} | {"Class ID".ljust(20)} | {"Class Time".ljust(20)} | {"Trainer".ljust(20)} | {"Exercise Type".ljust(20)}  ')
        print('-' * 115)

        # print body
        for i in range(num_rooms):
            cursor.execute(
                'SELECT class_id, class_time,  trainer_id, exercise_type   FROM Class WHERE room_num = %s AND class_time > current_timestamp', [i])
            results = cursor.fetchall()

            if len(results) == 0:
                print(
                    f'    {(" Room " + str(i)).ljust(20)} | {"-" * 20} | {"-" * 20} | {"-" * 20} | {"-" * 20} ')
                continue

            for thing in results:
                print(
                    f'    {(" Room " + str(i)).ljust(20)} | {str(thing[0]).ljust(20)} | {str(thing[1]).ljust(20)} | {str(thing[2]).ljust(20)} | {thing[3].ljust(20)}')

        print('-' * 115)

    def __get_all_equipment(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT equipment_id, name, room_num, maintenance_date FROM Equipment ORDER BY equipment_id')

        results = cursor.fetchall()
        if not results:
            print("No equipment.")
            return

        print("Equipment:")
        print(f'    {"Equipment ID".ljust(20)} | {"Name".ljust(20)} | {"Room Number".ljust(20)} | {"Maintenance Date".ljust(20)} ')
        print('-' * 95)
        for row in results:
            print(
                f'    {str(row[0]).ljust(20)} | {str(row[1]).ljust(20)} | {str(row[2]).ljust(20)} | {str(row[3]).ljust(20)} ')

        print('-' * 95)

    def __maintain_equipment(self, id):
        # simulates maintaining the equipment

        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE Equipment SET maintenance_date = CURRENT_TIMESTAMP WHERE equipment_id = %s', [id])
        self.conn.commit()

    def __bill_all(self):
        # for each member add monthly fee to amount owing
        cursor = self.conn.cursor()
        cursor.execute('SELECT username, monthly_fee FROM Club_Member')
        num = cursor.fetchone()

        for i in num:
            user, fee = i
            cursor.execute(
            'INSERT INTO Invoice(username, invoice_date, amount, invoiced_service, paid) VALUES (%s, NOW(), %s, %s, %s)', [user, fee, 'Membership Fee', 'false'])
            self.conn.commit()
