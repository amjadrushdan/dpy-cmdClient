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


def sterilise_content(content):
    """
    Sterilse everyone and here mentions in the provided string.
    Specifically, adds a zer width space after the `@` symbol
    when such a ping is detected.

    Parameters
    ----------
    content: str
        String to sterilise

    Returns: str
        Sterilsed string.
    """
    content = content.replace("@everyone", "@​everyone")
    content = content.replace("@here", "@​here")
    asciimsg = content.encode('ascii', errors='ignore').decode()
    if "@everyone" in asciimsg or "@here" in asciimsg:
        content = content.replace("@", "@​")

    return content
