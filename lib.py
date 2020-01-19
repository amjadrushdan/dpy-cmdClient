class SafeCancellation(Exception):
    default_msg = None

    def __init__(self, msg=None):
        self.msg = msg or self.default_msg


class UserCancelled(SafeCancellation):
    default_msg = "User cancelled the session!"


class ResponseTimedOut(SafeCancellation):
    default_msg = "Session timed out waiting for user response!"


class InvalidContext(Exception):
    """
    Throw when the context available doesn't match the context expected.
    """
    pass
