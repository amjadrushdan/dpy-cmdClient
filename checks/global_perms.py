from ..Check import check


@check(
    name="IS_OWNER",
    msg="You need to be a bot owner to use this command!"
)
async def is_owner(ctx, *args, **kwargs):
    return (ctx.author.id in ctx.client.owners)
