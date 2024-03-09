import asyncio
import time
import tkinter as tk
import re
from botpy import logging
from asyncio import TimerHandle
from dataclasses import dataclass
from io import BytesIO
from typing import Dict, List, NoReturn, Optional
from datetime import datetime
from threading import Timer
import time

from .utils import random_word, dic_list

from botpy.ext.command_util import Commands
from botpy import BotAPI
from botpy.message import Message

from .data_source import Wordle, GuessResult

game: Dict[str, Wordle] = {}
timers: Dict[str, TimerHandle] = {}
state = dict()

_log = logging.get_logger()


def check_word_input(text: str) -> bool:
    if re.match(r"^[a-zA-Z]{2,9}$", text):
        state["word"] = text
        return True
    return False


def start_game(cid, dic='CET6', length=5):
    word, meaning = random_word(word_length=length, dic_name=dic)
    game[cid] = Wordle(word, meaning)


def end_game(cid):
    del game[cid]


def pic(cid):
    im, ib = game[cid].draw()
    im.save(ib, 'png', quality=90)
    return ib.getvalue()


def pichint(cid, hint):
    im, ib = game[cid].draw_hint(hint)
    im.save(ib, 'png', quality=90)
    return ib.getvalue()


@Commands("wordle")
async def wordle(api: BotAPI, message: Message, params: str = None):
    dic, length = str, int
    cid = message.channel_id
    try:
        split = message.content.split("/wordle")[1]
        split = split.split(' ')
        if len(split) == 2:
            length = int(split[-1])
            dic = 'CET6'
        else:
            dic = split[-1].upper()
            del split[-1]
            length = int(split[-1])
    except (ValueError, IndexError):
        start_game(cid)
        await message.reply(content="你有6次机会猜出单词，单词长度为5\n"
                                    "@机器人后输入*后输入单词内容即可。限时5分钟。\n输入 *结束 以结束游戏\n输入 *提示 获得提示",
                            file_image=pic(cid))
        return
    if length < 3 or length > 8:
        await message.reply(content="❌请检查单词长度！")
        return
    if dic not in dic_list:
        await message.reply(content="字典错误，可使用的字典：" + ",".join(dic_list))
        return
    start_game(cid, dic, length)

    await message.reply(content=f"你有{game[cid].rows}次机会猜出单词，单词长度为{game[cid].length}\n"
                                f"@机器人后输入*后输入单词内容即可。\n输入 *结束 以结束游戏\n输入 *提示 获得提示",
                        file_image=pic(cid))


@Commands("*")
async def deal_wordle(api: BotAPI, message: Message, params: str = None):
    word = ''
    cid = message.channel_id

    if cid not in game:
        await message.reply(content="没有正在进行的游戏")
        return
    try:
        split = message.content.split('*')
        word = split[1]
    except IndexError:
        await message.reply(content="❌请检查你的输入")
    if word == '结束':
        msg = "已结束游戏"
        if len(game[cid].guessed_words) >= 1:
            msg += f'\n{game[cid].result}'
        await message.reply(content=msg)
        end_game(cid)
    if word == '提示':
        hint = game[cid].get_hint()
        if not hint.replace("*", ""):
            await message.reply(content="你还没有猜对过一个字母哦~再猜猜吧~")
            return
        await message.reply(file_image=pichint(cid, hint))
    if not check_word_input(word):
        return
    if len(word) != game[cid].length:
        await message.reply(content="请发送正确长度的单词")
        return
    result = game[cid].guess(word)
    if result in [GuessResult.WIN, GuessResult.LOSS]:
        await message.reply(content=(f"<@!{message.author.id}>恭喜你猜出了单词！" if result == GuessResult.WIN
                                     else "游戏结束\n很遗憾，没有人猜出单词呢") + f'\n{game[cid].result}',
                            file_image=pic(cid))
        end_game(cid)
    elif result == GuessResult.DUPLICATE:
        await message.reply(content="你已经猜过这个单词了哦")
    elif result == GuessResult.ILLEGAL:
        await message.reply(content=f"你确定{word}是一个合法的单词？")
    else:
        await message.reply(file_image=pic(cid))
