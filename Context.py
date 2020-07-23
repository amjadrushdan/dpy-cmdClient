import datetime
import discord
# from .logger import log
from . import lib

from . import cmdClient  # noqa
from .Command import Command  # noqa


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
        self.client = client  # type: cmdClient.cmdClient

        self.msg = kwargs.pop("message", None)  # type: str

        self.ch = self.msg.channel if self.msg is not None else kwargs.pop("channel", None)  # type: discord.Channel
        self.guild = self.msg.guild if self.msg is not None else kwargs.pop("guild", None)  # type: discord.Guild
        self.author = self.msg.author if self.msg is not None else kwargs.pop("author", None)  # type: discord.User

        self.arg_str = kwargs.pop("arg_str", None)  # type: str
        self.cmd = kwargs.pop("cmd", None)  # type: Command
        self.alias = kwargs.pop("alias", None)  # type: str

    @classmethod
    def util(cls, util_func):
        """
        Decorator to make a utility function available as a Context instance method
        """
        setattr(cls, util_func.__name__, util_func)


@Context.util
async def reply(ctx, content=None, allow_everyone=False, **kwargs):
    """
    Helper function to reply in the current channel.
    """
    if not allow_everyone:
        if content:
            content = lib.sterilise_content(content)

    return await ctx.ch.send(content=content, **kwargs)


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
