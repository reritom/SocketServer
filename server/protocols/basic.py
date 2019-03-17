class BasicProtocol:
    MAX_REPLIES = 1

    def __init__(self, connection):
        self.__connection = connection
        self.__replies_sent = 0

    def match(self, route) -> bool:
        # For a given route, determine if this request matches it
        return route.match(self.buffer)

    @classmethod
    def from_buffer(cls, buffer, connection):
        self = cls(connection)

        self.buffer = buffer
        self.parse_buffer(buffer)
        return self

    def reply(self, message, content_type='text'):
        if self.__replies_sent == self.MAX_REPLIES:
            raise Exception('Attempting to send reply number {} for a protocol which supports only {} replies'.format(self.__replies_sent, self.MAX_REPLIES))

        self.__connection.send(bytes(message, 'utf-8'))

    @property
    def pattern(self):
        return self.buffer

    @property
    def keep_alive(self):
        return True

    def parse_buffer(self, buffer):
        return
