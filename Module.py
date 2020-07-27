from typing import Type, Optional

from . import cmdClient
from .Command import Command
from .logger import log


class Module:
    name: str = "Base Module"

    def __init__(self, name: Optional[str] = None, baseCommand: Optional[Type[Command]] = Command):
        if name:
            self.name = name
        self.baseCommand = baseCommand

        self.cmds = []
        self.ready = False
        self.enabled = True

        self.launch_tasks = []
        self.init_tasks = []

        cmdClient.cmdClient.modules.append(self)

        log("New module created.", context=self.name)

    def cmd(self, name, cmdClass: Optional[Type[Command]] = None, **kwargs):
        """
        Decorator to create a command in this module with the given `name`.
        Creates the command using the provided `cmdClass`.
        Adds the command to the module command list and updates the client cache.
        Transparently passes the rest of the arguments to the `Command` constructor.
        """
        log("Adding command '{}'.".format(name), context=self.name)

        cmdClass = cmdClass or self.baseCommand

        def decorator(func):
            cmd = cmdClass(name, func, self, **kwargs)
            self.cmds.append(cmd)
            cmdClient.cmdClient.update_cmdnames()
            return cmd
        return decorator

    def attach(self, func):
        """
        Decorator which attaches the provided function to the current instance.
        """
        setattr(self, func.__name__, func)
        log("Attached '{}'.".format(func.__name__), context=self.name)

    def launch_task(self, func):
        """
        Decorator which adds a launch function to complete during the default launch procedure.
        """
        self.launch_tasks.append(func)
        log("Adding launch task '{}'.".format(func.__name__), context=self.name)
        return func

    def init_task(self, func):
        """
        Decorator which adds an init function to complete during the default initialise procedure.
        """
        self.init_tasks.append(func)
        log("Adding initialisation task '{}'.".format(func.__name__), context=self.name)
        return func

    def initialise(self, client):
        """
        Initialise hook.
        Executed by `client.initialise_modules`.
        """
        for task in self.init_tasks:
            task(client)

    async def launch(self, client):
        """
        Launch hook.
        Executed in `client.on_ready`.
        Must set `ready` to `True`, otherwise all commands will hang.
        """
        for task in self.launch_tasks:
            await task(client)

        self.ready = True

    async def pre_command(self, ctx):
        """
        Pre-command hook.
        Executed before a command is run.
        """
        pass

    async def post_command(self, ctx):
        """
        Post-command hook.
        Executed after a command is run without exception.
        """
        pass

    async def on_exception(self, ctx, exception):
        """
        Exception hook.
        Executed when a command function throws an exception.
        This is executed before "standard" exceptions are caught.
        """
        raise exception
        pass
