class Protocol:
    @classmethod
    def from_string(cls, string):
        return cls()

    def match(self, other_instance: Protocol) -> Bool:
        """
        Determine if this instance matches the other instance in whatever arbritrary manner seems fit
        """
        pass