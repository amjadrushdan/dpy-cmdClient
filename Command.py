import traceback
import asyncio

from .logger import log
from .Check import FailedCheck


class Command(object):
    def __init__(self, func, **kwargs):
        self.func = func

        self.hidden = kwargs.pop("hidden", False)
        self.short_help = kwargs.pop('short_help', None)
        self.long_help = func.__doc__ if func.__doc__ else None

        self.__dict__.update(kwargs)

    async def run(self, ctx):
        """
        Safely execute this command with the current context.
        Respond and log any exceptions that arise.
        """
        try:
            await self.func(ctx)
        except FailedCheck as e:
            log("Command failed check: {}".format(e.check.name), context=ctx.msg.id)
            if e.check.msg:
                await ctx.reply(e.check.msg)
        except asyncio.TimeoutError:
            log("Caught an unhandled TimeoutError", context=ctx.msg.id)
            await ctx.reply("Operation timed out")
        except Exception as e:
            full_traceback = traceback.format_exc()
            only_error = traceback.TracebackException.from_exception(e).format_exception_only()

            log("Caught the following exception while running command:\n{}".format(full_traceback),
                context=ctx.msg.id)

            await ctx.reply(
                ("An unexpected internal error occurred while running your command! "
                 "Please report the following error to the developer:\n`{}`").format(only_error)
            )

    def formatted_help(self, ctx):
        """
        Formats the long help of the current command and returns either a string or an embed.
        """
        return "```{}```".format(self.long_help)
