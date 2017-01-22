class ScheduledThread():

    def __init__(thread_definition):
        self.first = None
        self.repeat_multiple = None
        self.repeat_timespan = None
        self.title = None
        self.text = ""

        self.__parse_thread_definition(thread_definition)

    def __parse_thread_definition(thread_definition):

        # Split into lines, ignore first (blank)
        lines = thread_definition.split("\n")[1:]

    def is_valid(self):
        return not any(var is None for var in [self.title, self.repeat_multiple, self.repeat_timespan, self.first])