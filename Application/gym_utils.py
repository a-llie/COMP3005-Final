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
    def timestamp_add_hour(ts):
        dt = Utils.timestamp_to_datetime(ts)
        dt += timedelta(hours=1)
        return Utils.datetime_to_timestamp(dt)

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
        string = str(i) + ". | "
        for row in matrix:
            string += f" {row[0].ljust(row[1])} |"
        print(string)

    @staticmethod
    @dispatch(list, list, list, int, bool)
    def print_table(header, data, widths, header_width, numbered: bool = False):
        Utils.table_row_print(header)
        print("-" * header_width)
        j = 1
        for d in data:
            list = []
            for i, v in enumerate(d):
                list.append((str(v), widths[i]))
            if numbered:
                Utils.table_row_print(list, j)
                j += 1
            else:
                Utils.table_row_print(list)
        print("-" * header_width)

    @staticmethod
    def OK():
        input("OK [Enter]")

    @staticmethod
    def calculate_net(start: int, end: int):
        result = end - start
        if result > 0:
            return "+" + str(result)
        else:
            return str(result)
