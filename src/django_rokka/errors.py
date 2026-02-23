class RokkaError(Exception):
    def __init__(self, message):
        self.message = message  

class RokkaConfigError(RokkaError):
    def __init__(self, message):
        self.message = message  

class RokkaInvalidImageNameError(RokkaError):
    def __init__(self, message):
        self.message = message