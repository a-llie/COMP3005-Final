from System import System
from Person import Person
from gym_utils import Utils


class Member(Person):

    username: str
    weight: int

    def __init__(self, username, first_name, last_name, weight, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        self.username = username
        self.weight = weight

    def options(self, conn):
        options = [
            "Book a class or training session",
            "Update personal information",
            "View fitness achievements",
            "View health statistics",
            "See upcoming classes",
            "Log an exercise",
            "Exercise logbook",
            "Pay bill",
            "Sign Out"
        ]

        menu_choices = ""
        for i, option in enumerate(options):
            menu_choices += f"{i+1}. {option}\n"

        while True:
            menu_choice = input(
                f'{self.username}, choose an option: \n\n{menu_choices} \n\n>>')

            match menu_choice:
                case "1":
                    Utils.print_menu_header(options[0])
                    self.booking_choices(conn)
                case "2":
                    Utils.print_menu_header(options[1])
                case "3":
                    Utils.print_menu_header(options[2])
                case "4":
                    Utils.print_menu_header(options[3])
                case "5":
                    Utils.print_menu_header(options[4])
                    self.__see_upcoming_classes(conn)
                case "6":
                    Utils.print_menu_header(options[5])
                case "7":
                    Utils.print_menu_header(options[6])
                    self.__see_exercise_logbook(conn)
                case "8":
                    Utils.print_menu_header(options[7])
                    self.__pay_bill()
                case "9":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")
                    # self.options(conn)

    def booking_choices(self, conn):
        slot_choice = input(
            "Choose an option: \n 1. Book a class \n 2. Book a training session \n 3. Back \n\n>>")
        match slot_choice:
            case "1":
                print("<insert class booking here>")
            case "2":
                self.training_booking_process(conn)
            case "3":
                self.options(conn)
            case _:
                print("Invalid option. \n\n")
                self.booking_choices(conn)
                return

    def training_booking_process(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.user_weight FROM Club_Member c WHERE c.username = %s", [self.username])
        sessions = System.show_all_trainer_schedules(conn)
        self.browse_training_sessions(sessions, conn)

        session_choice = input(
            "Choose a session to book by entering the number: \n\n>>")
        session = sessions[int(session_choice) - 1]
        self.book_session(session, conn)

    def sign_in(conn):
        user = input("Enter your username: ")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT c.username, c.first_name, c.last_name, c.user_weight FROM Club_Member c WHERE c.username = %s", [user])
        found = cursor.fetchone()
        if found is None:
            print("User not found.\n")
            return
        else:
            user, first_name, last_name, weight = found
            return Member(user, first_name, last_name, weight, conn)

    def add_exercise(startTime, duration, exercise_type: str, weight):
        # add a exercise to the database under the current user
        # use the helper
        pass

    def update_info():
        # allowe the user to update atributes about themselves
        pass

    def get_exercises():
        pass

    def get_fitness_achievements():
        # best of
        pass

    def get_health_statistics():
        # history
        pass

    def sign_up_for_class(class_id):
        pass

    @staticmethod
    def browse_training_sessions(sessions, conn):
        print("Here are all the available training sessions:")
        i = 0
        for session in sessions:
            i += 1
            cursor = conn.cursor()
            cursor.execute(
                "SELECT first_name, last_name FROM Employee WHERE employee_id = %s", [session[0]])

            employee_name = cursor.fetchone()
            print(
                f'    {i}. {employee_name[0]} {employee_name[1]}, {session[1]}')

    def book_session(self, session, conn, exersise="personal training"):

        print(f'Booking session with {session[0]} at {session[1]}...')

        cursor = conn.cursor()

        # find free room
        room_id = System.get_free_room(conn, session[1])

        print(f'Room {room_id} is available.')

        # book a one hour block of the schedule
        System.add_class(conn, room_id, session[1], session[0], 1, 1, exersise)

        cursor.execute(
            'SELECT class_id FROM Class WHERE room_num = %s AND class_time = %s', [room_id, session[1]])
        class_id = cursor.fetchone()[0]

        self.__add_exercise(conn, class_id, session[1], 60, exersise)

        cursor.execute(
            'SELECT * FROM Exercise WHERE username = %s', [self.username])

        print("Exercise booked successfully.")
        print("Here are your upcoming exercises:")
        for row in cursor.fetchall():
            print(row)

        cursor.execute(
            'DELETE FROM Schedule s WHERE s.employee_id = %s AND s.schedule_start = %s', [session[0], session[1]])
        conn.commit()

    def __see_upcoming_classes(self, conn):
        cursor = conn.cursor()

        # find all classes that user is registered in
        cursor.execute(
            'SELECT c.class_time, c.room_num, c.exercise_type FROM Class c WHERE c.class_id IN (SELECT e.class_id FROM Exercise e WHERE e.username = %s) AND c.class_time > current_timestamp', [self.username])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.\n")
            return

        print("\nUpcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Exercise Type".ljust(25)} | {"Trainer Name".ljust(25)} ')
        print('-' * 95)
        for row in results:
            cursor.execute(
                'SELECT e.first_name, e.last_name FROM Employee e WHERE e.employee_id = (SELECT c.trainer_id FROM Class c WHERE c.class_time = %s)', [row[0]])
            trainer_name = cursor.fetchone()
            print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {row[2].ljust(25)} | {(trainer_name[0] + " " + trainer_name[1]).ljust(25)}')

        print('-' * 95)

    def __see_exercise_logbook(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            'SELECT duration, exercise_date, exercise_type, weight FROM Exercise WHERE username = %s and exercise_date < current_timestamp', [self.username])

        print("Here are your exercises:")
        past = cursor.fetchall()
        if not past:
            print("No exercises logged yet.\n")
            return
        else:
            print(
                f'{"Date".ljust(20)} | {"Exercise Type".ljust(15)} | {"Duration".ljust(10)} | {"Weight".rjust(8)}')
            print('-' * 70)
            for row in past:
                print(
                    f'{str(row[1]).ljust(20)} | {row[2].ljust(15)} | {(str(int(row[0])) + " minutes").rjust(10)} | {(str(row[3]) + " pounds").rjust(8) if row[3] else "N/A".rjust(8)}')
            print("-" * 70 + "\n\n")

    def __add_exercise(self, conn, class_id, startTime, duration, exercise_type: str):
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Exercise (duration, exercise_date, exercise_type, class_id, username, weight) VALUES (%s, %s, %s, %s, %s, %s)', [duration, startTime, exercise_type, class_id, self.username, self.weight])
        conn.commit()
        pass

    def __pay_bill(self):
        # get owing
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT invoice_date, amount, invoiced_service, invoice_id FROM Invoice WHERE username = %s AND paid = false', [self.username])
        results = cursor.fetchall()

        if not results:
            print("\nNo outstanding bills.\n\n")
            input("OK [Enter]")
            return
        i = 1
        print(
            f'\n# |{"Invoice Date".ljust(20)} | {"Amount".ljust(10)} | {"Service".ljust(20)} ')
        print('-' * 55)
        for row in results:
            service = ""
            if row[2] is None:
                service = "Membership Fee"
            else:
                cursor = self.conn.cursor()
                cursor.execute(
                    'SELECT exercise_type FROM Class WHERE class_id = %s AND class_time < NOW()', [row[2]])
                service = cursor.fetchone()[0]
                if service is None:
                    continue

            print(
                f'{i} | {str(row[0]).ljust(20)} | {(str(row[1])).ljust(10)} | {service.ljust(20)}')
            i += 1

        print('-' * 55)

        choice = input(
            f'\nEnter the number of the invoice you would like to pay (0 to exit): \n>>')
        # ask to pay
        if choice == '0':
            return
        print("\nconnecting to payment service..")
        cursor.execute(
            'UPDATE Invoice SET paid = true WHERE invoice_id = %s', [results[int(choice) - 1][3]])
        self.conn.commit()
        print("Invoice paid.\n\n")
