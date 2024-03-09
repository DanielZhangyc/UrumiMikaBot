import os
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.user import Member

import asyncio
from botpy import Client, Intents
from botpy.message import Message
from botpy.guild import Guild
from botpy.channel import Channel

from plugins.RussiaRoulette import rr
from plugins.wordle import wordle, deal_wordle
from plugins.ping import ping
from plugins.jrys import jrys
from configs.config import config
from service.database import init, disconnect

_log = logging.get_logger()


class UrumiMikaBot(botpy.Client):
    async def on_ready(self):
        _log.info(f"robot 「{self.robot.name}」 on_ready!")

    async def on_guild_member_add(self, member: Member):
        _log.info("%s 加入频道" % member.nick)
        dms_payload = await self.api.create_dms(member.guild_id, member.user.id)
        _log.info("发送私信")
        await self.api.post_dms(dms_payload["guild_id"], content="welcome join guild", msg_id=member.event_id)

    async def on_guild_member_update(self, member: Member):
        _log.info("%s 更新了资料" % member.nick)

    async def on_guild_member_remove(self, member: Member):
        _log.info("%s 退出了频道" % member.nick)

    async def on_at_message_create(self, message: Message):
        _log.info(f'Receive message from {message.author.username}(id{message.author.id}):"{message.content}"')
        commands = {
            '/rr': rr,
            '/wordle': wordle,
            '*': deal_wordle,
            'ping': ping,
            'jrys': jrys
        }
        for cmd, handler in commands.items():
            if cmd in message.content:
                await handler(api=self.api, message=message)
                break


if __name__ == "__main__":
    try:
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(init())
        intents = botpy.Intents(public_guild_messages=True, guild_members=True, guilds=True)
        client = UrumiMikaBot(intents=intents)
        client.run(appid=config["appid"], secret=config["secret"])
    except KeyboardInterrupt:
        _log.info("Bot Quit")
    #     loop = asyncio.get_event_loop()
    #     # 执行coroutine
    #     loop.run_until_complete(disconnect())
