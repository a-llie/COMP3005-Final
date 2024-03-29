import psycopg2

from Application.Person import Person
from Application.System import System


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
                f'{self.trainer_ID}, choose an option: \n 1. Schedual management \n 2. View member \n 3. See upcoming classes. \n 4. Sign Out \n\n>>')

            match menu_choice:
                case "1":
                    #manage the Schedual table(only refereing to the trianer singed in)
                    pass
                case "2":
                    choice = input("Would you like to search by: \n 1. username \n 2. name")
                    match choice:
                        case "1":
                            user = input("Input username: ")
                            out = System.get_member(user, self.conn)
                            #dispaly
                            System.print_member(out)

                            input("")
                            return

                        case "2":
                            first = input("Input first name: ")
                            last = input("Input last name: ")
                            out = System.get_member(first, last, self.conn)
                            #dispaly
                            System.print_member(out)

                            input("")
                            return
                        case _:
                            print("Invalid option")
                            return
                    return
                case "3":
                    #see whats booked for you (in the class table )
                    self.__see_upcoming_classes()
                    pass    
                
                case "4":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")
                    return

    def __get_schedule(self):
        cursor = self.conn.cursor()

        # find all classes that user is registered in
        cursor.execute(
            'SELECT schedule_start, schedule_end FROM Schedule  WHERE c.employee_id = %d AND schedule_start > current_timestamp', [self.trainer_ID])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.")
            return

        print("Upcoming classes:")
        print(f'    {"Start Time".ljust(20)} | {"End time".ljust(20)} ')
        print('-' * 95)
        for row in results:
                print(
                f'    {str(row[0]).ljust(20)} | {str(row[1]).ljust(20)} ')

        print('-' * 50)

    def __add_availability(self, start, end): #psudo code
        # breack it into one our blocks
        duration = end - start #might need a object/function for this
        cursor = self.conn.cursor()

        for i in range(duration):
            next_time = start + 1 #this may need a function too
            try:
                cursor.execute(
                'INSERT INTO Schedule (employee_id, schedule_start, schedule_end) VALUES (%s, %s, %s)', [self.trainer_ID, start, next_time])

            except psycopg2.errors.UniqueViolation:
                pass
            
            start = next_time
      

    def __remove_availability(self, start, end): #psudo code
        # breack it into one our blocks
        duration = end - start #might need a object/function for this
        cursor = self.conn.cursor()

        for i in range(duration):
            next_time = start + 1 #this may need a function too
            try:
                cursor.execute(
                'DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s AND schedule_end = %s', [self.trainer_ID, start, next_time])

            except psycopg2.errors.UniqueViolation:
                pass
            
            start = next_time
    
    def __manage_schedual_table(self):
        while True:
            menu_choice = input('Would you like to: \n 1. Get schedule \n 2. Add availibility \n 3. Remove availability \n 4. Exit \n\n>>')

            match menu_choice:
                case "1":
                    self.__get_schedule()
                    input("")
                    return
                case "2":
                    #take start time in format
                    #take end time in format

                    self.__add_availability()
                    input("")
                    return
                case "3":
                    #take start time in format

                    #take end time in format
                    self.__remove_availability()
                    input("")
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
            'SELECT c.class_time, c.room_num, c.exercise_type, c.registered FROM Class c WHERE c.trainer_id = %d AND c.class_time > current_timestamp', [self.trainer_ID])

        results = cursor.fetchall()
        if not results:
            print("No upcoming classes.")
            return

        print("Upcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Exercise Type".ljust(25)} | {"# Registered".ljust(5)} ')
        print('-' * 95)
        for row in results:
                print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {row[2].ljust(25)} | {row[3].ljust(5)}')

        print('-' * 95)