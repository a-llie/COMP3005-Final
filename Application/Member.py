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

    def options(self):
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
                    self.booking_choices()
                case "2":
                    Utils.print_menu_header(options[1])
                case "3":
                    Utils.print_menu_header(options[2])
                case "4":
                    Utils.print_menu_header(options[3])
                    self.get_health_statistics()
                case "5":
                    Utils.print_menu_header(options[4])
                    self.__see_upcoming_classes()
                case "6":
                    Utils.print_menu_header(options[5])
                case "7":
                    Utils.print_menu_header(options[6])
                    self.__see_exercise_logbook()
                case "8":
                    Utils.print_menu_header(options[7])
                    self.__pay_bill()
                case "9":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")

    def booking_choices(self):
        slot_choice = input(
            "Choose an option: \n 1. Book a class \n 2. Book a training session \n 3. Back \n\n>>")
        match slot_choice:
            case "1":
                self.class_booking_process()
            case "2":
                self.training_booking_process()
            case "3":
                self.options()
            case _:
                print("Invalid option. \n\n")
                self.booking_choices()
                return

    def training_booking_process(self):
        sessions = System.get_all_trainer_schedules(self.conn)
        self.browse_training_sessions(sessions)

        session_choice = input(
            "Choose a session to book by entering the number: \n\n>>")
        session = sessions[int(session_choice) - 1]
        self.book_session(session)

    def class_booking_process(self):
        classes = System.get_all_available_classes(self.conn, self.username)
        self.browse_classes(classes)

        session_choice = input(
            "Choose a class to book by entering the number: \n\n>>")

        chosen_class = classes[int(session_choice) - 1]
        self.book_class(chosen_class)

    @staticmethod
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

    def get_health_statistics(self):
        # history
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT date, weight, cardio_time, lifting_weight FROM Health WHERE username = %s ORDER BY date', [self.username])

        print("Here are your health statistics:\n")

        results = cursor.fetchall()
        Utils.print_table(
            [("Date", 20), ("Weight", 10), ("Cardio Time", 15), ("Lift Weight", 11)], results, [20, 10, 15, 11], 68)

        print("\n\nNet Change: \n")

        weight_change = Utils.calculate_net(results[0][1], results[-1][1])
        cardio_change = Utils.calculate_net(results[0][2], results[-1][2])
        lift_change = Utils.calculate_net(results[0][3], results[-1][3])

        Utils.table_row_print(
            [("Weight Change", 20), ("Cardio Change", 20), ("Lift Change", 11)])
        print('-' * 60)
        Utils.table_row_print(
            [(weight_change + " lbs", 20), (cardio_change + " minutes", 20), ((lift_change + " lbs"), 11)])
        print('-' * 60 + "\n\n")
        Utils.OK()

    def browse_training_sessions(self, sessions):
        print("Here are all the available training sessions:\n")
        i = 0
        Utils.table_row_print(
            [(" #", 2), ("Trainer Name", 25), ("Session Time", 20)])
        print(f'{"-"*55}')
        for session in sessions:
            i += 1
            employee_name = Utils.trainer_id_to_name(session[0], self.conn)
            Utils.table_row_print(
                [(str(i), 2), (employee_name[0] + " " + employee_name[1], 25), (str(session[1]), 20)])
        print(f'{"-"*55}\n')

    def browse_classes(self, sessions):
        print("Here are all the available classes\n")
        i = 0
        Utils.table_row_print(
            [(" #", 2), ("Trainer Name", 25), ("Session Time", 20)])
        print(f'{"-"*55}')
        for session in sessions:
            i += 1
            employee_name = Utils.trainer_id_to_name(session[5], self.conn)
            Utils.table_row_print(
                [(str(i), 2), (employee_name[0] + " " + employee_name[1], 25), (str(session[0]), 20)])
        print(f'{"-"*55}\n')

    # data step of booking a personal training session
    def book_session(self, session, exersise="personal training"):

        print(f'Booking session with {session[0]} at {session[1]}...')

        cursor = self.conn.cursor()

        # find free room
        room_id = System.get_free_room(self.conn, session[1])

        # book a one hour block of the schedule
        System.add_class(
            self.conn, room_id, session[1], session[0], 1, 1, exersise, 50)

        cursor.execute(
            'SELECT class_id FROM Class WHERE room_num = %s AND class_time = %s', [room_id, session[1]])
        class_id = cursor.fetchone()[0]

        self.__add_exercise(class_id, session[1], 60, exersise)

        print("Session booked successfully.\n")
        input("OK [Press Enter]")

        cursor.execute(
            'SELECT * FROM Exercise WHERE username = %s AND exercise_date > NOW()', [self.username])

        self.__see_upcoming_classes()

        cursor.execute(
            'DELETE FROM Schedule s WHERE s.employee_id = %s AND s.schedule_start = %s', [session[0], session[1]])
        self.conn.commit()

    def book_class(self, chosen_class):
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE Class SET registered = registered + 1 WHERE class_id = %s', [chosen_class[6]])

        print(chosen_class)
        self.conn.commit()
        self.__add_exercise(
            chosen_class[6], chosen_class[0], 60, chosen_class[3])

        System.create_class_invoice(self.conn, self.username, chosen_class[6])

        print("Class booked successfully. You will be invoiced after the class has taken place. \n")
        self.__see_upcoming_classes()

    def __see_upcoming_classes(self):
        cursor = self.conn.cursor()

        # find all classes that user is registered in
        cursor.execute(
            'SELECT c.class_time, c.room_num, c.exercise_type FROM Class c WHERE c.class_id IN (SELECT e.class_id FROM Exercise e WHERE e.username = %s) AND c.class_time > current_timestamp ORDER BY c.class_time ASC', [self.username])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.\n")
            return

        full_results = []
        print("\n Upcoming classes:\n")
        for row in results:
            cursor.execute(
                'SELECT e.first_name, e.last_name FROM Employee e WHERE e.employee_id = (SELECT c.trainer_id FROM Class c WHERE c.class_time = %s)', [row[0]])
            trainer_name = cursor.fetchone()
            row = list(row)
            row.append(trainer_name[0] + " " + trainer_name[1])
            full_results.append(row)

        Utils.print_table(
            [("Class Time", 20), ("Room Number", 15), ("Exercise Type", 25), ("Trainer Name", 25)], full_results, [20, 15, 25, 25], 95)

        print("\n")
        Utils.OK()

    def __see_exercise_logbook(self):
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT exercise_date, exercise_type, duration FROM Exercise WHERE username = %s and exercise_date < current_timestamp', [self.username])

        print("Here are your previously logged exercises:\n")
        past = cursor.fetchall()
        if not past:
            print("No exercises logged yet.\n")
            return
        else:
            Utils.print_table(
                [("Date", 20), ("Exercise Type", 15),
                 ("Duration", 10)], past, [20, 15, 10], 54)
            print("\n")
            Utils.OK()

    def __add_exercise(self, class_id, startTime, duration, exercise_type: str):
        cursor = self.conn.cursor()
        cursor.execute(
            'INSERT INTO Exercise (duration, exercise_date, exercise_type, class_id, username) VALUES (%s, %s, %s, %s, %s)', [duration, startTime, exercise_type, class_id, self.username])
        self.conn.commit()
        pass

    def __pay_bill(self):
        # get owing
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT invoice_date, amount, invoiced_service, invoice_id FROM Invoice WHERE username = %s AND paid = false AND invoice_date <NOW()', [self.username])
        results = cursor.fetchall()

        if not results:
            print("\nNo outstanding bills.\n\n")
            input("OK [Enter]")
            return

        full_results = []
        for row in results:
            service = ""
            if row[2] is None:
                new_row = [row[0], row[1], 'Membership Fee']
                full_results.append(new_row)

            else:
                cursor = self.conn.cursor()
                cursor.execute(
                    'SELECT exercise_type FROM Class WHERE class_id = %s AND class_time < NOW()', [row[2]])
                service = cursor.fetchone()
                if service is None:
                    service = ["N/A"]
                new_row = [row[0], row[1], service[0]]
                full_results.append(new_row)

        Utils.print_table(
            [("#", 0), ("Invoice Date", 21), ("Amount", 10),
             ("Service", 15)], full_results, [20, 10, 15], 57, True
        )

        choice = input(
            f'\nEnter the number of the invoice you would like to pay (0 to exit): \n>>')
        # ask to pay
        if choice == '0':
            return

        print(results[int(choice) - 1][3])
        print("\nconnecting to payment service..")
        cursor.execute(
            'UPDATE Invoice SET paid = true WHERE invoice_id = %s', [results[int(choice) - 1][3]])
        self.conn.commit()
        print("Invoice paid.\n\n")
        Utils.OK()
