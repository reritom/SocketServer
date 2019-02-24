class HTTPProtocol:
    HTTP_POST = "POST"
    HTTP_PATCH = "PATCH"
    HTTP_PUT = "PUT"
    HTTP_GET = "GET"
    HTTP_DELETE = "DELETE"

    def __init__(self, connection):
        self.connection = connection

    @classmethod
    def from_buffer(cls, buffer, connection):
        self = cls(connection)

        self.buffer = buffer
        self.parse_buffer(buffer)
        return self

    def reply(self, message):
        pass

    def parse_buffer(self, buffer):
        lines = buffer.split('\n')

        # Parse the first line
        header_line = lines.pop(0).split(' / ')
        method = header_line[0]
        http_version = header_line[1].split('/')[1]

        headers = {}

        # Iterate over the header
        for index, line in enumerate(lines):
            if line == ' ':
                # We've reached the end of the header
                break

            print("Splitting line {}".format(line))
            try:
                split_line = line.split(': ')
                headers[split_line[0]] = split_line[1].strip()
            except:
                print("Line {} of len {} cannot be split".format(line, len(line)))
                break

        # If we aren't posting data, we've reached the end
        if method in [self.HTTP_POST, self.HTTP_PATCH]:
            pass

        print("Method {}, version {}".format(method, http_version))
        print("Headers are {}".format(headers))