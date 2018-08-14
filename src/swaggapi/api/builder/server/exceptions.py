class ServerError(Exception):
    def __init__(self, details, model, response):
        self.details = details
        self.model = model
        self.response = response
        super(ServerError, self).__init__(self.details)

    def encode(self):
        return {
            "details": self.details,
            "expected": str(self.model),
            "actual": self.response
        }


class BadRequest(Exception):
    pass

