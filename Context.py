import datetime
import discord
# from .logger import log


class Context(object):
    __slots__ = (
        'client',
        'msg',
        'ch',
        'guild',
        'objects',
        'arg_str',
        'cmd',
        'alias',
        'author'
    )

    def __init__(self, client, **kwargs):
        self.client = client

        self.msg = kwargs.pop("message", None)

        self.ch = self.msg.channel if self.msg is not None else kwargs.pop("channel", None)
        self.guild = self.msg.guild if self.msg is not None else kwargs.pop("guild", None)
        self.author = self.msg.author if self.msg is not None else kwargs.pop("author", None)

        self.arg_str = kwargs.pop("arg_str", None)
        self.cmd = kwargs.pop("cmd", None)
        self.alias = kwargs.pop("alias", None)

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


@Context.util
async def error_reply(ctx, error_str):
    """
    Notify the user of a user level error.
    Typically, this will occur in a red embed, posted in the command channel.
    """
    embed = discord.Embed(
        colour=discord.Colour.red(),
        description=error_str,
        timestamp=datetime.datetime.utcnow()
    )
    try:
        return await ctx.ch.send(embed=embed)
    except discord.Forbidden:
        return await ctx.reply(error_str)
