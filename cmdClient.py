import imp
import sys
import os
import traceback
import logging
import asyncio
from bisect import bisect

import discord

from .logger import log
from .Command import Command
from .Context import Context


# List of current active `Command`s
cmds = []

# Cache of current command names associated to commands, of the form {cmdname: Command}
cmd_cache = {}


def update_cache():
    """
    Updates the command cache.
    """
    for cmd in cmds:
        cmd_cache[cmd.name] = cmd

        for alias in cmd.aliases:
            cmd_cache[alias] = cmd


# Command decorator for adding new commands to cmds
def cmd(name, **kwargs):
    def decorator(func):
        cmd = Command(name, func, **kwargs)
        # Add command if it doesn't exist already
        if cmd.name not in cmd_cache:
            cmds.append(cmd)
        update_cache()

        return func

    return decorator


class cmdClient(discord.Client):
    def __init__(self, prefix, owners=None):
        super().__init__()
        self.prefix = prefix
        self.owners = owners or []
        self.objects = {}

        self.cmds = cmds
        self.cmd_cache = cmd_cache

    async def on_ready(self):
        """
        Client has logged into discord and completed initialisation.
        Log a ready message with some basic statistics and info.
        """
        ready_str = (
            "Logged in as {client.user}\n"
            "User id {client.user.id}\n"
            "Logged in to {guilds} guilds\n"
            "------------------------------\n"
            "Prefix is '{prefix}'\n"
            "Loaded {commands} commands\n"
            "------------------------------\n"
            "Ready to take commands!\n"
        ).format(
            client=self,
            guilds=len(self.guilds),
            prefix=self.prefix,
            commands=len(cmds)
        )
        log(ready_str)

    async def on_error(self, event_method, *args, **kwargs):
        """
        An exception was caught in one of the event handlers.
        Log the exception with a traceback, and continue on.
        """
        log("Ignoring exception in {}\n{}".format(event_method, traceback.format_exc()),
            level=logging.ERROR)

    async def on_message(self, message):
        """
        Handle incoming messages.
        If the message contains a valid command, pass the message to run_cmd
        """
        # Check whether the message starts with the set prefix
        content = message.content.strip()
        if not content.startswith(self.prefix):
            return

        # If the message starts with a valid command, pass it along to run_cmd
        content = content[len(self.prefix):].strip()
        cmdnames = [cmdname for cmdname in cmd_cache if content[:len(cmdname)].lower() == cmdname]
        cmdname = max(cmdnames, key=len)

        if cmdname is not None:
            await self.run_cmd(message, cmdname, content[len(cmdname):].strip())

    async def run_cmd(self, message, cmdname, arg_str):
        """
        Run a command and pass it the command message and the arg_str.

        Parameters
        ----------
        message: discord.Message
            The original command message.
        cmdname: str
            The name of the command to execute.
        arg_str: str
            The remaining content of the command message after the prefix and command name.
        """
        log(("Executing command '{cmdname}' "
             "from user '{message.author}' ({message.author.id}) "
             "in guild '{message.guild}' ({guildid}).\n"
             "{content}").format(
                 cmdname=cmdname,
                 message=message,
                 guildid=message.guild.id if message.guild else None,
                 content='\n'.join(('\t' + line for line in message.content.splitlines()))),
            context=message.id
            )
        cmd = cmd_cache[cmdname]

        # Build the context
        ctx = Context(
            client=self,
            message=message,
            arg_str=arg_str,
            alias=cmdname,
            cmd=cmd
        )

        try:
            await cmd.run(ctx)
        except Exception:
            log("The following exception encountered executing command '{}'.\n{}".format(cmdname,
                                                                                         traceback.format_exc()),
                context=message.id,
                level=logging.ERROR)

    def load_dir(self, dirpath):
        """
        Import all modules in a directory.
        Primarily for the use of importing new commands.
        """
        loaded = 0
        initial_cmds = len(cmds)

        for fn in os.listdir(dirpath):
            path = os.path.join(dirpath, fn)
            if fn.endswith(".py"):
                sys.path.append(dirpath)
                module = imp.load_source("bot_module_" + str(fn), path)
                sys.path.remove(dirpath)

                if "load_into" in dir(module):
                    module.load_into(self)

                loaded += 1
        log("Imported {} modules from '{}', with {} new commands!".format(loaded, dirpath, len(cmds)-initial_cmds))

    def add_after_event(self, event, func, priority=0):
        """
        Add an event handler to execute after the central event handler.

        Parameters
        ----------
        event: str
            Name of a valid discord.py event.
        func: Function(Client, ...)
            Function taking the client as its first argument, and the event parameters as the rest
        priority: int
            Priority indiciating which order the event handlers should be executed.
            The core event handler is always executed first.
            After that, handlers are executed in order of increasing priority.
        """
        async def new_func(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except Exception:
                log(
                    ("Exception encountered executing event handler '{}' for event '{}'. "
                     "Traceback:\n{}").format(
                         func.__name__,
                         event,
                         traceback.format_exc()
                     ), level=logging.ERROR
                )

        after_handler = "after_" + event
        if not hasattr(self, after_handler):
            setattr(self, after_handler, [])
        handlers = getattr(self, after_handler)
        handlers.insert(bisect([handler[1] for handler in handlers], priority), (new_func, priority))
        log("Adding after_event handler \"{}\" for event \"{}\" with priority \"{}\"".format(
            func.__name__, event, priority
        ))

    def dispatch(self, event, *args, **kwargs):
        super().dispatch(event, *args, **kwargs)
        after_handler = "after_"+event
        if hasattr(self, after_handler):
            for handler in getattr(self, after_handler):
                asyncio.ensure_future(handler[0](self, *args, **kwargs), loop=self.loop)
