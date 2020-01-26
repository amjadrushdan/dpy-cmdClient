import logging
import traceback
import asyncio
import textwrap

from .logger import log
from .Check import FailedCheck
from .lib import SafeCancellation


class Command(object):
    def __init__(self, name, func, **kwargs):
        self.name = name
        self.func = func

        self.aliases = kwargs.pop("aliases", [])
        self.hidden = kwargs.pop("hidden", False)
        self.short_help = kwargs.pop('short_help', None)
        self.long_help = self.parse_help()

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
                await ctx.error_reply(e.check.msg)
        except SafeCancellation as e:
            log("Caught a safe command cancellation: {}: {}".format(e.__class__.__name__, e.msg))

            if e.msg is not None:
                await ctx.error_reply(e.msg)
        except asyncio.TimeoutError:
            log("Caught an unhandled TimeoutError", context=ctx.msg.id, level=logging.WARNING)

            await ctx.error_reply("Operation timed out.")
        except Exception as e:
            full_traceback = traceback.format_exc()
            only_error = "".join(traceback.TracebackException.from_exception(e).format_exception_only())

            log("Caught the following exception while running command:\n{}".format(full_traceback),
                context=ctx.msg.id,
                level=logging.ERROR)

            await ctx.reply(
                ("An unexpected internal error occurred while running your command! "
                 "Please report the following error to the developer:\n`{}`").format(only_error)
            )

    def parse_help(self):
        """
        Convert the docstring of the command function into a list of (fieldname, fieldcontent) tuples.
        """
        if not self.func.__doc__:
            return []

        # Split the docstring into lines
        lines = textwrap.dedent(self.func.__doc__).strip().splitlines()
        help_fields = []
        field_name = ""
        field_content = []

        for line in lines:
            if line.endswith(':'):
                # New field!
                if field_content:
                    # Add the previous field to the table
                    field = textwrap.dedent("\n".join(field_content))
                    help_fields.append((field_name, field))

                # Initialise the new field
                field_name = line[:-1].strip()
                field_content = []
            else:
                # Add the line to the current field content
                field_content.append(line)

        # Add the last field to the table if it exists
        if field_content:
            # Add the previous field to the table
            field = textwrap.dedent("\n".join(field_content))
            help_fields.append((field_name, field))

        return help_fields
