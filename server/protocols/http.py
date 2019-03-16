class HTTPProtocol:
    HTTP_POST = "POST"
    HTTP_PATCH = "PATCH"
    HTTP_PUT = "PUT"
    HTTP_GET = "GET"
    HTTP_DELETE = "DELETE"

    MAX_REPLIES = 1

    def __init__(self, connection):
        self.__connection = connection
        self.__replies_sent = 0
        self.payload = None
        self.headers = None

    @classmethod
    def from_buffer(cls, buffer, connection):
        self = cls(connection)

        self.buffer = buffer
        self.parse_buffer(buffer)
        return self

    def reply(self, message, content_type='text'):
        if self.__replies_sent == MAX_REPLIES:
            raise Exception('Attempting to send reply number {} for a protocol which supports only {} replies'.format(self.__replies_sent, self.MAX_REPLIES))

        if content_type == 'json':
            if isinstance(message, dict):
                message = json.dumps(message)

        header = 'HTTP/1.1 200 OK\r\nCache-Control: no-cache, private\r\nContent-Length: {}\r\nDate: Mon, 24 Nov 2014 10:21:21 GMT\r\n\r\n'.format(len(bytes(message, 'utf-8')))
        self.__connection.send(header)
        self.__connection.send(message)

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

        self.headers = headers
        self.method = method

        # If we aren't posting data, we've reached the end
        if method in [self.HTTP_POST, self.HTTP_PATCH]:
            self.payload = {}
            pass

        print("Method {}, version {}".format(method, http_version))
        print("Headers are {}".format(headers))
