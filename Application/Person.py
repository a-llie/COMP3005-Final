from abc import abstractmethod
import psycopg2
from psycopg2 import sql
import multipledispatch
from gym_utils import Utils
from System import System


class Person():
    first_name: str
    last_name: str
    conn: psycopg2._psycopg.connection

    def __init__(self, first_name, last_name, conn) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.conn = conn

    @abstractmethod
    def options(self):
        pass

    def search_for_user(self, username: bool):
        if username:
            user = input("Input username: ")
            out = System.find_members(user, self.conn)
        else:
            first = input(
                "First name: (blank to skip) >>")
            last = input(
                "Last name: (blank to skip) >> ")
            match first, last:
                case "", "":
                    out = System.find_members(
                        "", "", self.conn)
                case _, "":
                    out = System.find_members(
                        first, "", self.conn)
                case "", _:
                    out = System.find_members(
                        "", last, self.conn)
                case _, _:
                    out = System.find_members(
                        first, last, self.conn)

        if out == [] or out is None:
            print("No users found. \n")
            return

        chosen_user = self.__choose_user_from_list(out)

        if chosen_user == False:
            return

        System.print_member(out[chosen_user-1])

    @staticmethod
    def __choose_user_from_list(out: list):
        if len(out) > 1:
            list = []
            for user in out:
                list.append([(user[0]), user[3], user[4]])

            Utils.print_table(
                [("# ", 0), ("Username", 15), ("First Name", 20), ("Last Name", 20)], list, [15, 20, 20], True)

            while True:
                chosen_user = Utils.prompt_for_number(
                    "Choose a user from above. >> ")

                if chosen_user < 1 or chosen_user > len(out):
                    print("Invalid choice.")
                    continue
                break
            return chosen_user
        else:
            return 1

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

    def search_for_member(self):
        Utils.print_menu_header("View Member")
        while True:
            choice = input(
                "Would you like to search by: \n 1. username \n 2. name \n")
            match choice:
                case "1":
                    Utils.print_menu_header("Search by Username")
                    self.search_for_user(True)
                    break
                case "2":
                    Utils.print_menu_header("Search by name")
                    self.search_for_user(False)
                    break
                case _:
                    print("Invalid option.\n")
                    continue
