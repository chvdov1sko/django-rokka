class RokkaImageUploadError(Exception):
    def __init__(self, message):
        self.message = message

class RokkaImageDeleteError(Exception):
    def __init__(self, message):
        self.message = message

class RokkaImageNotFoundError(Exception):
    def __init__(self, message):
        self.message = message

class RokkaConfigError(Exception):
    def __init__(self, message):
        self.message = message        
