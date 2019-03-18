class HTTPMatcher:
    @staticmethod
    def match(route, protocol_instance):
        # For a given route, determine if this request matches it
        return route.match(protocol_instance.url) and protocol_instance.method in route.methods
