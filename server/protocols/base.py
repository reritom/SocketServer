class BaseProtocol:
    def reply(self, *args, **kwargs):
        raise NotImplementedError()
