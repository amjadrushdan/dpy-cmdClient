# from .logger import log


class Context(object):
    __slots__ = (
        'client',
        'msg',
        'ch',
        'guild',
        'objects',
        'cmd'
    )

    def __init__(self, client, **kwargs):
        self.client = client

        self.msg = kwargs.get("message", None)

        self.ch = self.msg.channel if self.msg is not None else kwargs.get("channel", None)
        self.guild = self.msg.guild if self.msg is not None else kwargs.get("guild", None)

    @classmethod
    def util(cls, util_func):
        """
        Decorator to make a utility function available as a Context instance method
        """
        setattr(cls, util_func.__name__, util_func)


@Context.util
async def reply(ctx, *args, **kwargs):
    """
    Helper function to reply in the current channel.
    TODO: Some output protection for everyone and here pings.
    """
    return await ctx.ch.send(*args, **kwargs)
