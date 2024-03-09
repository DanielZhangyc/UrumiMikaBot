import openpyxl


class Word:
    def __init__(self, word, trans):
        self.word = word
        self.translation = trans


# 读取 Excel 文件
workbook = openpyxl.load_workbook('words.xlsx')
sheet = workbook.active

word_objects = []

# 逐行读取数据并保存到 Word 对象中
for row in sheet.iter_rows(values_only=True):
    word_objects.append(Word(row[0], row[1]))


def get_word_list():
    return word_objects


# 打印 Word 对象列表
# for word_obj in word_objects:
#     print(word_obj.word, "-", word_obj.translation)

word_list = []
with open("SUM_of_cet4+6+toefl+gre.txt", 'r') as file:
    for line in file:
        word = line.strip()  # 去除空格和换行符
        word_list.append(word)


def get_huge_word_list():
    return word_list
