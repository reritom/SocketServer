class BasicMatcher:
    @staticmethod
    def match(route, protocol_instance) -> bool:
        # For a given route, determine if this request matches it
        return route.match(protocol_instance.buffer)
