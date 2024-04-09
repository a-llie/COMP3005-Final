from datetime import datetime, timedelta
from multipledispatch import dispatch


class Utils():
    @staticmethod
    def print_menu_header(option: str):
        print(f'\n{"-"*len(option)}\n{option}\n{"-"*len(option)}\n')

    @staticmethod
    def timestamp_to_datetime(ts) -> datetime:
        f = '%Y-%m-%d %H:%M:%S'
        return datetime.strptime(ts, f)

    @staticmethod
    def datetime_to_timestamp(dt: datetime):
        f = '%Y-%m-%d %H:%M:%S'
        return dt.strftime(f)

    @staticmethod
    def get_datetime(header: str):
        print(header)
        year = Utils.prompt_for_number("Year:")
        month = Utils.prompt_for_number("Month (number):")
        day = Utils.prompt_for_number("Day:")

        hour = Utils.prompt_for_number("Hour (24-h clock):")
        minute = Utils.prompt_for_number("Minute:")
        return datetime(year, month, day, hour, minute, 0)

    @staticmethod
    def timestamp_add_hour(ts):
        dt = Utils.timestamp_to_datetime(ts)
        dt += timedelta(hours=1)
        return Utils.datetime_to_timestamp(dt)
    
    @staticmethod
    def datetime_add_hour(dt):
        dt += timedelta(hours=1)
        return dt

    @staticmethod
    def prompt_for_number(prompt: str):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("\nInvalid input.\n")

    @staticmethod
    def trainer_id_to_name(id: int, conn):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT first_name, last_name FROM Employee WHERE employee_id = %s", [id])
        return cursor.fetchone()

    @staticmethod
    @dispatch(list)
    def table_row_print(matrix: list):
        string = ""
        for row in matrix:
            string += f" {row[0].ljust(row[1])} |"
        print(string)

    @staticmethod
    @dispatch(list, int)
    def table_row_print(matrix: list, i: int):
        string = ""
        if i < 10:
            string = str(i) + ".  |"
        elif i >= 10 and i < 100:
            string = str(i) + ". |"
        else:
            string = str(i) + ".|"
        for row in matrix:
            string += f" {row[0].ljust(row[1])} |"
        print(string)

    @staticmethod
    def print_table(header, data, widths, numbered: bool = False):
        Utils.table_row_print(header)
        header_width = sum(widths) + 3*(len(widths))
        if numbered:
            header_width += 4
        print("-" * header_width)
        j = 1
        for d in data:
            list = []
            if type(d) != str:
                for i, v in enumerate(d):
                    list.append((str(v), widths[i]))
            else:
                list.append((d, header_width))
            if numbered:
                Utils.table_row_print(list, j)
                j += 1
            else:
                Utils.table_row_print(list)
        print("-" * header_width)

    @staticmethod
    def OK():
        input("\nOK [Enter]\n")

    @staticmethod
    def calculate_net(start: int, end: int):
        result = end - start
        if result > 0:
            return "+" + str(result)
        else:
            return str(result)

    @staticmethod
    def prompt_for_number(prompt: str):
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("\nInvalid input.\n")

    @staticmethod
    def prompt_for_non_blank(prompt: str):
        while True:
            result = input(prompt)
            if result == "":
                print("\nInvalid input.\n")
                continue
            return result

    @staticmethod
    def number_to_month(number: int):
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        return months[number-1]
