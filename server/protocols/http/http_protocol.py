import json

class HTTPProtocol:
    HTTP_POST = "POST"
    HTTP_PATCH = "PATCH"
    HTTP_PUT = "PUT"
    HTTP_GET = "GET"
    HTTP_DELETE = "DELETE"

    MAX_REPLIES = 1

    def __init__(self, connection):
        self._connection = connection
        self.__replies_sent = 0
        self.payload = None
        self.headers = None

    @classmethod
    def from_buffer(cls, buffer, connection):
        self = cls(connection)

        self.buffer = buffer
        self.parse_buffer(buffer)
        return self

    def reply(self, message, content_type=None):
        if self.__replies_sent == self.MAX_REPLIES:
            raise Exception('Attempting to send reply number {} for a protocol which supports only {} replies'.format(self.__replies_sent, self.MAX_REPLIES))

        if content_type is not None:
            if content_type == 'json':
                if isinstance(message, dict):
                    message = json.dumps(message)
        else:
            if isinstance(message, dict):
                message = json.dumps(message)

        header = 'HTTP/1.1 200 OK\r\nCache-Control: no-cache, private\r\nContent-Length: {}\r\nDate: Mon, 24 Nov 2014 10:21:21 GMT\r\n\r\n'.format(len(bytes(message, 'utf-8')))
        self._connection.send(bytes(header, 'utf-8'))
        self._connection.send(bytes(message, 'utf-8'))

    @property
    def pattern(self):
        return self.url

    @property
    def keep_alive(self):
        try:
            return self.headers['Connection'] == 'keep-alive'
        except:
            return True

    def parse_buffer(self, buffer):
        print(buffer)
        lines = buffer.split('\n')

        # Parse the first line
        try:
            header_line = lines.pop(0).split(' ')
            self.method = header_line[0]
            self.url = header_line[1]
            self.http_version = header_line[2].split('/')[1]
        except Exception as e:
            #print("Failed to parse the first line of the request {}".format(e))
            pass

        self.headers = {}

        # Iterate over the header
        for index, line in enumerate(lines):
            if line == ' ':
                # We've reached the end of the header
                break

            #print("Splitting line {}".format(line))
            try:
                split_line = line.split(':', 1)
                self.headers[split_line[0]] = split_line[1].strip()
            except Exception as e:
                #print("Line {} of len {} cannot be split: {}".format(line, len(line), e))
                break

        # If we aren't posting data, we've reached the end
        if self.method in [self.HTTP_POST, self.HTTP_PATCH]:
            self.payload = {}
            pass

        #print("Method {}, version {}".format(self.method, self.http_version))
        #print("Headers are {}".format(self.headers))
