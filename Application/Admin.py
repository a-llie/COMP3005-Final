

from Application.Person import Person
from Application.System import System


class Admin(Person):

    def __init__(self, first_name, last_name, conn) -> None:
        Person.__init__(self, first_name, last_name, conn)
        return
        

    def options(self):
        while True:
            menu_choice = input(
                f'{self.trainer_ID}, choose an option: \n 1. View member \n 2. Manage Rooms. \n 3. Manage Equipment \n 4. Manage Upcoming Classes \n 5. Manage Billing \n 6. Sign Out \n\n>>')

            match menu_choice:

                case "1":
                    choice = input("Would you like to search by: \n 1. username \n 2. name")
                    match choice:
                        case "1":
                            user = input("Input username: ")
                            out = System.get_member(user, self.conn)
                            #dispaly
                            System.print_member(out)

                            input("")
                            continue
                            

                        case "2":
                            first = input("Input first name: ")
                            last = input("Input last name: ")
                            out = System.get_member(first, last, self.conn)
                            #dispaly
                            System.print_member(out)

                            input("")
                            continue
                            
                        case _:
                            print("Invalid option")
                            
                    
                case "2":
                    #add a ability to toggle a romm so that it cant be booked?
                    self.__view_rooms()

                case "3":
                    choice = input("Would you like to: \n 1. View Equipment \n 2. Service Equipment")
                    match choice:
                        case "1":
                            
                            self.__get_all_equipment()                            
                            continue
                            

                        case "2":
                            id = input("Input equipment ID: ")
                            
                            self.__maintain_equipment(id)                            
                            continue
                            
                        case _:
                            print("Invalid option")

                case "4":
                    choice = input("Would you like to: \n 1. View Upcoming Classes \n 2. Add a Class \n 3. Remove a Class(by time and trainer) \n 4. Remove a Class(by class id)")
                    match choice:
                        case "1":
                            
                            self.__get_class_schedule()                            
                            continue
                            

                        case "2":
                            trainer = input("Who will teach the class: ")
                            time = input("What time will the class be: ")
                            exercise = input(f"What will {trainer} be teaching: ")
                            cap = input("What is the capacity: ")
                            if cap is None:
                                self.__add_class(trainer, time, exercise)
                            self.__add_class(trainer, time, exercise, cap)
                                                  
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
                    #bill
                    pass
                case "6":
                    print("Signing out...\n\n")
                    return
                case _:
                    print("Invalid option")
                    


    def __get_trainer_schedule(self, id):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT schedule_start, schedule_end FROM Schedule  WHERE c.employee_id = %d AND schedule_start > current_timestamp', [id])

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


    def __get_class_schedule(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT c.class_time, c.room_num, c.trainer_id, c.exercise_type, c.registered, c.capacity FROM Class c AND c.class_time > current_timestamp', [self.trainer_ID])

        results = cursor.fetchall()
        if not results:
            print("Nothing Scheduled.")
            return

        print("Upcoming classes:")
        print(f'    {"Class Time".ljust(20)} | {"Room Number".ljust(15)} | {"Room Number".ljust(20)} | {"Exercise Type".ljust(20)} | {"Registered".ljust(5)} | {"Capacity".ljust(5)} ')
        print('-' * 95)
        for row in results:
                print(
                f'    {str(row[0]).ljust(20)} | {(" Room " + str(row[1])).ljust(15)} | {row[2].ljust(20)} | {row[3].ljust(20)} | {row[4].ljust(5)} | {row[5].ljust(5)}')

        print('-' * 95)


    def __add_class(self, trainer_id, start, exercise, capacity=5):
        cursor = self.conn.cursor()

        # remove that block from the free scedual of the trainer
        cursor.execute('DELETE FROM Schedule WHERE employee_id = %s AND schedule_start = %s', [trainer_id, start])
        self.conn.commit()

        # pick a free room (in system.py)
        room_id = System.get_free_room(self.conn, start)
        #creat class
        System.add_class(self.conn, room_id, start, trainer_id, capacity, 0, exercise )


    def __remove_class(self, start, id):
        cursor = self.conn.cursor()

        #romovce all exercises that have the class as a foren key
        #get the class id
        cursor.execute('SELECT class_id FROM Class WHERE class_time = %s AND trainer_id = %s', [start, id])
        class_id = cursor.fetchone()[0]

        cursor.execute('DELETE FROM Exercise WHERE class_id = %s', [class_id])
        self.conn.commit()

        #remove the class
        cursor.execute('DELETE FROM Class WHERE class_time = %s AND trainer_id = %s', [start, id])
        self.conn.commit()


    def __remove_class(self, class_id):
        cursor = self.conn.cursor()

        #romovce all exercises that have the class as a foren key
        cursor.execute('DELETE FROM Exercise WHERE class_id = %s', [class_id])
        self.conn.commit()

        #remove the class
        cursor.execute('DELETE FROM Class WHERE class_id = %s' , [class_id])
        self.conn.commit()

    def __view_rooms(self):
        #view what rooms were booked and by what classes
        #search class and take the room and class, but also lifst rooms that arn't booked
        cursor = self.conn.cursor()
        cursor.execute('SELECT num_rooms FROM Building')
        num_rooms = cursor.fetchone()[0]

        #header
        print("Rooms in Building 1:") #CURRENTLY HARD CODDED
        print(f'     {"Room Number".ljust(15)} | {"Class ID".ljust(10)} | {"Class Time".ljust(20)} | {"Trainer".ljust(20)} | {"Exercise Type".ljust(20)}  ')
        print('-' * 95)

        #print body
        for i in range(num_rooms):
            cursor.execute(
            'SELECT class_id, class_time,  trainer_id, exercise_type   FROM Class WHERE room_num = %s AND class_time > current_timestamp', [i])
            results = cursor.fetchall()

            if not results:
                print(
                f'    {(" Room " + str(i)).ljust(15)} | {'-' * 20} | {'-' * 20} | {'-' * 20} ')
                continue
            
            print(
            f'    {(" Room " + str(i)).ljust(15)} | {str(results[0]).ljust(20)} | {results[1].ljust(20)} | {results[2].ljust(20)} ')

        print('-' * 95)
        

    def __get_all_equipment(self):
        cursor = self.conn.cursor()

        cursor.execute(
            'SELECT equipment_id, name, room_num, maintenance_date FROM Equipment')

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
        pass


    def __bill_all():
        pass

    def __bill_member(username):
        pass
