class Person():
    first_name: str
    last_name: str
    username: str

    def __init__(self, first_name, last_name, username) -> None:
        self.first_name = first_name
        self.last_name = last_name
        self.username = username

        print(f'Person {self.first_name} {self.last_name} created.')
