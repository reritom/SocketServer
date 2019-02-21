class Caller:
    def __init__(self, connection, raw):
        self._connection = connection
        self.raw = raw

    def reply(self, message):
        if not isinstance(message, bytes):
            try:
                message = str(message)
                message = bytes(message, 'utf-8')
            except:
                print("Failed to convert reply to sendable format")

        try:
            self._connection.send(message)
        except:
            print("Failed to send reply")