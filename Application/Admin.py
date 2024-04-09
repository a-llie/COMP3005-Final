

from Person import Person
from System import System
from gym_utils import Utils
from datetime import datetime


class Admin(Person):

    def __init__(self, first_name, last_name, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        return

    @staticmethod
    def sign_in(conn):
        id = Utils.prompt_for_number("Enter your employee ID: ")
        print("\n")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.first_name, c.last_name FROM Employee c WHERE c.employee_id = %s AND c.is_trainer = FALSE", [id])
        found = cursor.fetchone()
        return found

    def options(self):
        while True:
            Utils.print_menu_header("Admin Menu")
            choices = [
                "View member",
                "View Upcoming Room Usage",
                "Manage Equipment",
                "Manage Upcoming Classes",
                "Manage Billing",
                "Sign Out"
            ]

            menu_options = ""
            for i, option in enumerate(choices):
                menu_options += f"{i+1}. {option}\n"

            menu_choice = input(
                f'{self.first_name}, choose an option: \n{menu_options} \n\n>>')

            match menu_choice:

                case "1":
                    self.search_for_member()
                    Utils.OK()

                case "2":
                    # add a ability to toggle a romm so that it cant be booked?
                    Utils.print_menu_header("Future Room Usage")
                    self.__view_rooms()
                    Utils.OK()

                case "3":
                    Utils.print_menu_header("Manage Equipment")
                    choice = input(
                        "Would you like to: \n 1. View Equipment \n 2. Service Equipment.\n>>")
                    match choice:
                        case "1":
                            Utils.print_menu_header("View Equipment")
                            self.__get_all_equipment()
                            Utils.OK()
                            continue

                        case "2":
                            Utils.print_menu_header("Service Equipment")
                            self.__maintain_equipment()
                            Utils.OK()
                            continue

                        case _:
                            print("Invalid option.")
                            Utils.OK()

                case "4":
                    Utils.print_menu_header("Manage Upcoming Classes")
                    choice = input(
                        "Would you like to: \n 1. View Upcoming Classes \n 2. Add a Class \n 3. Remove a Class\n>>")
                    match choice:
                        case "1":
                            Utils.print_menu_header("View Upcoming Classes")
                            self.__get_class_schedule()
                            Utils.OK()
                            continue

                        case "2":
                            Utils.print_menu_header("Add a Class")
                            while True:
                                trainer = Utils.prompt_for_number(
                                    "ID of trainer who will teach the class: ")
                                cursor = self.conn.cursor()
                                cursor.execute(
                                    'SELECT employee_id, first_name FROM Employee WHERE employee_id = %s AND is_trainer = true', [trainer])
                                result = cursor.fetchone()
                                if not result:
                                    print("Trainer not found.")
                                    Utils.OK()
                                    continue
                                break

                            name = result[1]

                            cursor = self.conn.cursor()
                            cursor.execute(
                                'SELECT schedule_start FROM Schedule s WHERE s.employee_id = %s AND s.schedule_start > current_timestamp AND (SELECT  COUNT(*) FROM Class c WHERE c.class_time = s.schedule_start) < %s ORDER BY schedule_start ', [result[0], 8])

                            schedules = cursor.fetchall()

                            if not schedules:
                                print("Trainer has no availability.")
                                Utils.OK()
                                continue

                            print("Trainer's availability:")

                            Utils.print_table(
                                [("#", 0), ("Time", 20)], schedules, [20], True)

                            time = -1
                            while time < 1 or time > len(schedules):
                                time = Utils.prompt_for_number(
                                    "Select a timeslot from above for the class.>>")

                            exercise = input(
                                f"What will {name} be teaching? >> ")

                            cap = Utils.prompt_for_number(
                                "What is the class capacity? >> ")
                            price = Utils.prompt_for_number(
                                "What is the price? >> ")

                            timeslot = schedules[time-1][0]
                            self.__add_class(
                                trainer, timeslot, exercise, price, cap)
                            continue
                        case "3":
                            classes = System.get_all_available_classes(
                                self.conn)

                            if not classes:
                                print("No classes available.")
                                Utils.OK()
                                continue

                            self.browse_classes(classes)

                            class_id = -1
                            while class_id < 1 or class_id > len(classes):
                                class_id = Utils.prompt_for_number(
                                    "Choose a class by its listed number from above to remove. >> ")
                                if (class_id < 1 or class_id > len(classes)):
                                    print("Invalid choice.")
                                    continue

                            self.__remove_class(classes[class_id - 1][-1])

                        case _:
                            print("Invalid option.\n")

                case "5":
                    Utils.print_menu_header("Manage Billing")
                    choice = input(
                        "1. See outstanding bills.\n2. Bill all members for this month's membership.\n\n>>")
                    match choice:
                        case "1":
                            Utils.print_menu_header("Outstanding Bills")
                            self.__see_outstanding_bills()
                        case "2":
                            self.__bill_all()
                    Utils.OK()
                case "6":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option.\n")

    def __get_class_schedule(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity FROM Class c WHERE c.class_time > current_timestamp ORDER BY class_time')

        results = cursor.fetchall()
        if not results:
            print("Nothing Scheduled.\n")
            return

        Utils.print_table(
            [("Class Time", 20), ("Room Number", 12), ("Trainer ID", 15), ("Exercise Type", 20), ("Registered", 10), ("Capacity", 10)], results, [20, 12, 15, 20, 10, 10])

    def __add_class(self, trainer_id, start, exercise, price, capacity=5):
        cursor = self.conn.cursor()

        # pick a free room (in system.py)
        room_id = System.get_free_room(self.conn, start)

        if room_id is None:
            print("No rooms available at that time.")
            return

        # creat class
        System.add_class(self.conn, room_id, start, trainer_id,
                         capacity, 0, exercise, price)

        # remove that block from the free scedual of the trainer
        cursor.execute('DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s', [
                       trainer_id, start])

        self.conn.commit()

    def __remove_class(self, class_id):
        cursor = self.conn.cursor()

        # romovce all exercises that have the class as a foreign key
        cursor.execute('DELETE FROM Exercise WHERE class_id = %s', [class_id])

        # delete all related invoices
        cursor.execute(
            'DELETE FROM Invoice WHERE invoiced_service = %s', [class_id])

        # remove the class
        cursor.execute(
            'SELECT trainer_id, class_time FROM Class WHERE class_id = %s', [class_id])

        results = cursor.fetchone()
        if not results:
            print("Class not found.")
            return

        cursor.execute('DELETE FROM Class WHERE class_id = %s', [class_id])

        # add the time back to the trainers schedule
        cursor.execute(
            'INSERT INTO Schedule (employee_id, schedule_start) VALUES (%s, %s)', [results[0], results[1]])

        print("Class removed.\n")
        self.conn.commit()

    def __view_rooms(self):
        # view what rooms were booked and by what classes
        # search class and take the room and class, but also lifst rooms that arn't booked
        cursor = self.conn.cursor()
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        results = []

        for i in range(1, num_rooms+1):
            cursor.execute(
                'SELECT class_id, class_time,  trainer_id, exercise_type FROM Class WHERE room_num = %s AND class_time > current_timestamp ORDER BY class_time', [i])
            result = cursor.fetchall()
            for row in result:
                trainer = Utils.trainer_id_to_name(row[2], self.conn)
                results.append(
                    (f'Room {i}', row[0], row[1], trainer[0] + " " + trainer[1], row[3]))

        if len(results) == 0:
            print("No classes scheduled.")
            Utils.OK()
            return

        Utils.print_table(
            [("Room Number", 15), ("Class ID", 10), ("Class Time", 20), ("Trainer", 30), ("Exercise Type", 25)], results, [15, 10, 20, 30, 25])

    def __get_all_equipment(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT equipment_id, name, room_num, maintenance_date FROM Equipment ORDER BY equipment_id')

        results = cursor.fetchall()
        if not results:
            print("No equipment found.")
            Utils.OK()
            return

        Utils.print_table(
            [("Equipment ID", 20), ("Type", 20), ("Room Number", 20), ("Maintenance Date", 20)], results, [20, 20, 20, 20])

    def __get_equipment_maintenace_needed(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT equipment_id, name, room_num, maintenance_date FROM Equipment WHERE maintenance_date < current_timestamp -  INTERVAL %s ORDER BY maintenance_date', ('1 MONTH',))

        results = cursor.fetchall()
        if not results:
            return None

        Utils.print_table(
            [("Equipment ID", 20), ("Name", 20), ("Room Number", 20), ("Maintenance Date", 20)], results, [20, 20, 20, 20])

        return results

    def __maintain_equipment(self):
        # simulates maintaining the equipment
        equipment = self.__get_equipment_maintenace_needed()
        if not equipment:
            print("All maintenace up to date.")
            return

        choice = input(
            "1. Perform maintenance on all equipment listed above. \n2. Perform maintenance on a specific piece of equipment. \n3. Cancel. \n\n>>")
        match choice:
            case "1":
                cursor = self.conn.cursor()
                cursor.execute(
                    'UPDATE Equipment SET maintenance_date = DATE_TRUNC(%s, current_timestamp) WHERE maintenance_date < current_timestamp -  INTERVAL %s', ['day', '1 MONTH'])
                self.conn.commit()
                print("All equipment has been serviced.\n")
                return
            case "2":
                id = Utils.prompt_for_number("Input equipment ID: ")
                cursor = self.conn.cursor()
                cursor.execute(
                    'UPDATE Equipment SET maintenance_date = DATE_TRUNC(%s, current_timestamp) WHERE equipment_id = %s', ['day', id])

                self.conn.commit()

                cursor.execute(
                    'SELECT equipment_id, name, room_num, maintenance_date FROM Equipment WHERE equipment_id = %s', [id])

                result = cursor.fetchone()

                if not result:
                    print("Equipment not found.\n")
                    return

                print(f'Equipment {result[1]} has been serviced.\n')

                Utils.print_table(
                    [("Equipment ID", 20), ("Name", 20), ("Room Number", 20), ("Maintenance Date", 20)], [result], [20, 20, 20, 20])

                return
            case "3":
                return
            case _:
                print("Invalid option.\n")

    def __bill_all(self):
        # for each member add monthly fee to amount owing
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO Invoice (invoice_date, username, amount, invoiced_service, paid)
                    SELECT 
                        DATE_TRUNC('month', CURRENT_DATE) AS invoice_date,
                        c.username,
                        c.monthly_fee,
                        null AS invoiced_service,
                        false AS paid
                    FROM 
                        Club_Member c
                    WHERE not exists
                       (SELECT * FROM Invoice i WHERE i.username = c.username AND i.invoice_date = DATE_TRUNC('month', CURRENT_DATE) AND i.invoiced_service is null)
                        AND c.membership_type != 'Cancelled'""")

        self.conn.commit()
        print(
            f"All members have been billed for {Utils.number_to_month(datetime.now().month)} {datetime.now().year}.\n")

    def __see_outstanding_bills(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT i.username, i.amount, i.invoice_date, i.invoiced_service FROM Invoice i WHERE paid = false AND ((SELECT class_time FROM Class c WHERE c.class_id = i.invoiced_service ) < NOW() OR i.invoiced_service is null) ORDER BY invoice_date')

        results = cursor.fetchall()
        if not results:
            print("No outstanding bills.\n")
            return

        final_results = []

        for row in results:
            if row[3] is None:
                final_results.append(
                    [row[0], row[1], row[2], 'Membership Fee'])
            else:
                cursor.execute(
                    'SELECT exercise_type FROM Class WHERE class_id = %s', [row[3]])
                exercise = cursor.fetchone()[0]
                final_results.append([row[0], row[1], row[2], exercise])

        Utils.print_table(
            [("Username", 20), ("Amount", 20), ("Invoice Date", 20), ("Invoiced Service", 20)], final_results, [20, 20, 20, 20])
