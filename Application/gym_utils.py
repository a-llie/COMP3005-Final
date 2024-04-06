from datetime import datetime, timedelta


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
