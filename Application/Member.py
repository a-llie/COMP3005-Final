from System import System
from Person import Person


class Member(Person):

    username: str
    weight: int

    def __init__(self, username, first_name, last_name, weight) -> None:
        Person.__init__(self, first_name, last_name, username)
        self.weight = weight

    def options(self, conn):
        while True:
            menu_choice = input(
                f'{self.username}, choose an option: \n 1. Book a class or training session \n 2. Update personal information \n 3. View fitness achievements \n 4. View health statistics \n 5. See upcoming classes. \n 6. Exercise logbook. \n 7. Sign Out \n\n>>')

            match menu_choice:
                case "1":
                    self.booking_choices(conn)
                case "2":
                    print("<insert update info here>")
                case "3":
                    print("<insert fitness achievements here>")
                case "4":
                    print("<insert health statistics here>")
                case "5":
                    self.__see_upcoming_classes(conn)
                case "6":
                    self.__see_exercise_logbook(conn)
                case "7":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")
                    self.options(conn)
                    return

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

    def sign_in():
        pass

    # member
    def register():
        # insert feilds and submit
        pass

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
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        for i in range(num_rooms):
            cursor.execute(
                'SELECT c.room_num FROM Class c WHERE c.room_num = %s AND c.class_time = %s', [i, session[1]])
            if not cursor.fetchone():
                room_id = i
                break

        print(f'Room {room_id} is available.')

        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO Class (room_num, class_time, trainer_id, capacity, registered, exercise_type) VALUES (%s, %s, %s, %s, %s, %s)', [room_id, session[1], session[0], 1, 1, exersise])
        # books a one hour block of the schedule
        conn.commit()

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
            print("No upcoming classes.")
            return

        print("Upcoming classes:")
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
            print("No exercises logged yet.")
            return
        else:
            date_tag = "Date"
            exercise_tag = "Exercise Type"
            duration_tag = "Duration"
            weight_tag = "Weight"

            print(
                f'{date_tag.ljust(20)} | {exercise_tag.ljust(15)} | {duration_tag.ljust(10)} | {weight_tag.rjust(8)}')
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
