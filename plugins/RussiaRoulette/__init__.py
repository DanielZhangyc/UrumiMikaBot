import random

from botpy.ext.command_util import Commands
from botpy import BotAPI
from botpy.message import Message


class RrGame:
    bullet = int
    mute_time = int
    index = int

    def __init__(self, bullet, mute_time, index):
        self.bullet = bullet
        self.mute_time = mute_time
        self.index = index


game = dict()
bullet_not_shoot = ["哒哒哒... 大胆的家伙，你没挂！",
                    "砰！你躲过了死亡的威胁，运气不错。",
                    "你紧闭双眼，但是无事发生。",
                    "可惜，这次没有击中。",
                    "命运对你微笑着。",
                    "空膛，今天是你的幸运日。",
                    "你真胆大，可惜没有中枪。"
                    ]
bullet_shoot = ['随着一声枪响，你应声倒地。',
                '你结束了悲壮的一生。']


def init_game(id):
    game[id] = RrGame(
        bullet=random.randint(1, 6),
        mute_time=random.randint(1, 2),
        index=1
    )


def end_game(id):
    del game[id]


@Commands("rr")
async def rr(api: BotAPI, message: Message, params: str = None):
    id = message.channel_id
    if id not in game:
        init_game(id)
    if game[id].index == game[id].bullet:
        content = bullet_shoot[random.randint(0, 1)] + f'({game[id].index}/6)'
        await message.reply(content=content)
        await api.mute_member(guild_id=message.guild_id, user_id=message.author.id,
                              mute_seconds=str(game[id].mute_time * 60))
        end_game(id)
    else:
        content = bullet_not_shoot[random.randint(0, 6)] + f'({game[id].index}/6)'
        await message.reply(content=content)
        game[id].index += 1
