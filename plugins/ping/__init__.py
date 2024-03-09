from botpy.ext.command_util import Commands
from botpy import BotAPI
from botpy.message import Message


@Commands("ping")
async def ping(api: BotAPI, message: Message, params: str = None):
    content = 'pong!'
    split = message.content.split('/ping')
    if len(split) >= 2:
        content += split[1]
    await message.reply(content=content)
