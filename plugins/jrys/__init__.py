import random
import time
import apscheduler

from botpy import BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message

events_list = ['看涩图', '明日方舟', '雀魂', '舞萌', 'mc', '中二节奏', '音击', '🫎关', '超群主', '女装', '干饭', '表白',
               '原神', '写代码', '打比赛', '抄作业']


def get_event(num_do: int, num_not_do):
    hash_table = dict()
    do_list, not_do_list = [], []
    i = 0
    while i < num_do:
        randid = random.randint(0, len(events_list) - 1)
        if randid in hash_table:
            continue
        else:
            hash_table[randid] = True
            i = i + 1
            do_list.append(events_list[randid])

    while i < num_not_do:
        randid = random.randint(0, len(events_list) - 1)
        if randid in hash_table:
            continue
        else:
            hash_table[randid] = True
            i = i + 1
            not_do_list.append(events_list[randid])
    return do_list, not_do_list


class User:
    def __init__(self):
        self.lucky = random.randint(0, 100)
        self.do_list, self.not_do_list = get_event(random.randint(0, 5), random.randint(0, 5))


def create_message(user: User) -> str:
    message = ''
    message = message + f'今天是{time.strftime("%m月%d日", time.localtime())}\n'
    message = message + f'你今天的幸运值是{user.lucky}\n'
    for i in user.do_list:
        message = message + f"宜 {i}\n"
    for i in user.not_do_list:
        message = message + f"忌 {i}\n"

    message = message + '❤️ UrumiMikaBot ❤️'

    return message


today_user = dict()


@Commands("jrys")
async def jrys(api: BotAPI, message: Message, params: str = None):
    if message.author.id not in today_user:
        today_user[message.author.id] = User()
    user = today_user[message.author.id]
    await message.reply(content=f"<@!{message.author.id}>" + create_message(user))
