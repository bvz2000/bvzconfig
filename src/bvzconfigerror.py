class ConfigError(Exception):
    """
    Asset exception
    """

    def __init__(self, message, errno=0):

        super(ConfigError, self).__init__()

        self.code = errno
        self.message = message

    @property
    def errno(self):
        return self.code
