import arrow
from itertools import islice

class ScheduledThread:

    def __init__(self, thread_definition):
        self.first = None
        self.repeat_multiple = None
        self.repeat_timespan = None
        self.title = None
        self.text = ""

        self.__parse_thread_definition(thread_definition)

    def __parse_thread_definition(self, thread_definition):

        # Split into lines, ignore first (blank)
        lines = thread_definition.split("\n")[1:]

        text_start_index = None

        for index, line in enumerate(lines):
            components = line.split(": ")
            key = components[0]
            value = components[1]

            # Update attributes, but break as soon as we find text
            # as it spans over multiple lines
            if not "text" in key:

                value = value.strip()

                if key == "first":
                    self.first = arrow.get(value)

                elif key == "repeat":
                    repeat_components = value.split(" ")

                    # Shortest format: "1 day" = 5 chars
                    if len(repeat_components) == 2 and len(value) > 5:
                        multiple = int(repeat_components[0])
                        timespan = repeat_components[1]

                        if multiple > 0 or timespan in ["hour","day","week","month"]:
                            self.repeat_multiple = multiple
                            self.repeat_timespan = timespan

                elif key == "sticky":
                    self.sticky = (value == "true")

                elif key == "title":
                    self.title = value[1:-1] #Remove quotes (first/last characters)
            else:
                text_start_index = index
                break

        if text_start_index is not None:

            for line in islice(lines, text_start_index+1, None):
                self.text += f"\n{line.strip()}\n"

    def is_valid(self):
        return not any(var is None for var in [self.title, self.repeat_multiple, self.repeat_timespan, self.first])