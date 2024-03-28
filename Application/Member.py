

class Member():

    curr_username: str

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
        # use the helper
        pass

    def book_session(trainer_id, start_time, exersise=""):
        # books a one hour block of the scedual
        # the scedual is subtractive so when you book a private session remove the block
        # add a class at that time wish that trainer with capacity of one and registred one
        pass

    # private
    def __add_exercise(class_id, startTime, duration, exercise_type: str, weight):
        pass
