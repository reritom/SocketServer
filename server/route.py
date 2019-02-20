import re

class Route:
    def __init__(self, pattern, callback):
        self.callback = callback
        self.pattern = pattern
        self.regex = self.regex_from_pattern(pattern)
        print("Pattern {} has regex {}".format(pattern, self.regex))

    @staticmethod
    def regex_from_pattern(pattern):
        param_open = False
        index = 0
        re_buffer = ''
        placeholder_buffer = ''
        placeholder_list = []
        re_placeholder = '(?P<{}>.*)'

        while index < len(pattern):
            if param_open:
                if pattern[index] == '>':
                    print("In close in param open")
                    re_buffer +=  re_placeholder.format(placeholder_buffer)
                    placeholder_list.append(placeholder_buffer)
                    print("Placeholder buffer {}".format(placeholder_buffer))
                    placeholder_buffer = ''
                    print("Rebuffer {}".format(re_buffer))
                    param_open = False
                else:
                    placeholder_buffer += pattern[index]

            elif pattern[index] == '<':
                print("Opening param")
                param_open = True

            elif pattern[index] == '>':
                print("Closing param")
                param_open = False

            else:
                re_buffer += pattern[index]
                print("Rebuffer {}".format(re_buffer))

            index += 1

        return re.compile(re_buffer)


    def match(self, value) -> bool:
        """
        Check if the value matches the pattern
        """
        return self.regex.match(value)