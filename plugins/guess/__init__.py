import random
import re

from botpy.ext.command_util import Commands
from botpy import BotAPI
from botpy.message import Message

from plugins.guess.read_file import get_word_list
from plugins.guess.read_file import get_huge_word_list
from plugins.wordle.utils import spell


class TargetWord:
    word = str
    trans = str

    def __init__(self, word, trans):
        self.word = word
        self.trans = trans


class Word_game:
    status = bool
    word = TargetWord
    correct = set()
    wrong = set()
    user_chance = list()
    winner = str

    def __init__(self, status, word, correct, wrong, user_chance, winner):
        self.word = word
        self.status = status
        self.correct = correct
        self.wrong = wrong
        self.user_chance = user_chance
        self.winner = winner


game = dict()
word_list = get_word_list()
big_word_list = get_huge_word_list()


def init_words() -> TargetWord:
    global word_list
    rand_num = random.randint(1, 2220)
    word = word_list[rand_num].word
    trans = word_list[rand_num].translation
    return TargetWord(
        word=word,
        trans=trans
    )


def start_game(channel_id):
    global game
    game[channel_id] = Word_game(
        status=True,
        word=init_words(),
        correct=set(),
        wrong=set(),
        user_chance=dict(),
        winner=str
    )


def end_game(channel_id):
    if channel_id not in game:
        return
    else:
        del game[channel_id]


def summon_output(require: str, game: Word_game):
    ret = ''
    if require == 'correct':
        for i in game.correct:
            ret = ret + f'{i} '

    elif require == 'wrong':
        for i in game.wrong:
            ret = ret + f'{i} '

    elif require == 'line':
        for i in game.word.word:
            if i in game.correct:
                ret = ret + f'{i} '
            else:
                ret = ret + f'_ '
    elif require == 'statistic':
        for i in game.user_chance:
            ret = ret + f'🔘{i} - {game.user_chance[i]}\n'
    return ret


def output(require: str, game: Word_game) -> str:
    message = str
    if require == 'during':
        message = (f"✨{game.word.trans}\n"
                   f"🟢正确的字母:{summon_output('correct', game)}\n"
                   f"🔴错误的字母:{summon_output('wrong', game)}\n"
                   f"📝{summon_output('line', game)}")

    if require == 'end':
        message = (f'⛔️正确答案是:"{game.word.word}"\n'
                   f'{game.word.trans}')

    if require == 'correct':
        message = (f"✅恭喜你！回答正确！\n"
                   f'正确答案是:"{game.word.word}"\n'
                   f'{game.word.trans}')

    if require == "statistic":
        message = f'以下是统计数据（次数）\n'
        message += summon_output('statistic', game)

    return message


def check_input(text: str):
    pattern = r'^[a-zA-Z]+$'  # 定义只能由大小写字母组成的模式

    if re.match(pattern, text):
        return True
    else:
        return False


@Commands("guess")
async def guess(api: BotAPI, message: Message, params: str = None):
    global game
    id = message.channel_id
    if id not in game:
        start_game(message.channel_id)
    else:
        await message.reply(content=f"<@!{message.author.id}>已有一个正在进行的猜词游戏！")
        return False

    await message.reply(content=f"<@!{message.author.id}>猜词游戏开始！@机器人并在#后输入单词内容即可参与。输入#end结束")

    await message.reply(content=output('during', game[id]))


@Commands("#")
async def detect(api: BotAPI, message: Message, params: str = None):
    id = message.channel_id
    global game
    if id not in game:
        await message.reply(content="没有正在进行的游戏")
        return

    split = message.content.split('#')
    guess = split[1]
    guess = guess.lower()

    if guess == 'end':
        await message.reply(content=output('end', game[id]))
        await message.reply(content=output('statistic', game[id]))
        end_game(id)
        return
    if not check_input(guess):
        return
    elif not spell.unknown((guess,)):
        await message.reply(content="无法在词典中找到该单词。")
        return

    for ch in guess:
        if ch in game[id].word.word:
            game[id].correct.add(ch)
        else:
            game[id].wrong.add(ch)

    if message.author.username not in game[id].user_chance:
        game[id].user_chance[message.author.username] = 1
    else:
        game[id].user_chance[message.author.username] += 1

    if guess == game[id].word.word:
        game[id].winner = message.author.username
        await message.reply(content=output('correct', game[id]))
        await message.reply(content=f'😍本次游戏赢家:{game[id].winner}')
        await message.reply(content=output('statistic', game[id]))
        end_game(id)
    else:
        await message.reply(content=output('during', game[id]))
