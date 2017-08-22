import telebot
import sqlite3
from random import randint
from telebot import types

import config

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start'])
def start_command(message):
    if ((message.chat.type == 'group' or message.chat.type == 'supergroup') and message.text == '/start@EGEStress_bot') or message.chat.type == 'private':
        CurrentWord = DBChangeWord(message.chat.id)
        bot.send_message(message.chat.id, 'Привет, я стрессбот! Давай так: я тебе буду отправлять слова, а ты мне их будешь возвращать, но с одним ударным звуком. \r\nНапример: \r\n-звонить\r\n-звонИть \r\nЕсли я в группе, то, чтобы я мог проверить ваш ответ, пишите его при пересылке моего сообщения с помощью "Reply"')
#        bot.send_message(message.chat.id, config.listof_testwords[CurrentWord])
        WordSplit(CurrentWord, message.chat.id)

@bot.message_handler(commands=['cword'])
def cword_command(message):
    if ((message.chat.type == 'group' or message.chat.type == 'supergroup') and message.text == '/cword@EGEStress_bot') or message.chat.type == 'private':
        CurrentWord = DBWhichWord(message.chat.id)
        WordSplit(CurrentWord, message.chat.id)
#        bot.send_message(message.chat.id, config.listof_testwords[CurrentWord])

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if ((message.chat.type == 'group' or message.chat.type == 'supergroup') and message.text == '/stats@EGEStress_bot') or message.chat.type == 'private':
        bot.send_message(message.chat.id, DBCounter(message.chat.id))

@bot.message_handler(content_types=['text'])
def WordCheck(message):
    print(message.text)
    usedword = message.text.split(' ')[0]
    correct = DBWordCheck(message.chat.id, usedword)
    if correct == 1:
        bot.send_message(message.chat.id, 'Верно!')
        DBAddToCounter(message.chat.id, True)
        CurrentWord = DBChangeWord(message.chat.id)
#        bot.send_message(message.chat.id, config.listof_testwords[CurrentWord])
        WordSplit(CurrentWord, message.chat.id)
    elif correct == 2:
        DBAddUser(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Нет! Надо вот так: ' + config.listof_correctwords[correct])
        DBAddToCounter(message.chat.id, False)
        CurrentWord = DBChangeWord(message.chat.id)
#        bot.send_message(message.chat.id, config.listof_testwords[CurrentWord])
        WordSplit(CurrentWord, message.chat.id)

@bot.callback_query_handler(func=lambda call:True)
def ButtonWordCheck(call):
#    if call.message.message_id == DBLastMID(call.message.chat.id):
    correct = DBWordCheck(call.message.chat.id, call.data)
    if correct == 1:
        bot.send_message(call.message.chat.id, 'Верно!')
        DBAddToCounter(call.message.chat.id, True)
    elif correct == 2:
        DBAddUser(call.message.chat.id)
        return
    else:
        bot.send_message(call.message.chat.id, 'Нет! Надо вот так: ' + config.listof_correctwords[correct])
        DBAddToCounter(call.message.chat.id, False)
    CurrentWord = DBChangeWord(call.message.chat.id)
    #bot.send_message(call.message.chat.id, config.listof_testwords[CurrentWord])
    WordSplit(CurrentWord, call.message.chat.id)

def DBAddUser(user):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    word = randint(0, 454)
    cursor.execute('insert into hooy(User, CurrentWord, Wins, Loses) values(?,?,?,?)', (user, word, 0, 0))
    connection.commit()
    connection.close()
    return word

def DBChangeWord(user):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    cursor.execute('SELECT CurrentWord FROM hooy WHERE User = ?', (user,))
    a = cursor.fetchone()
    if a is None:
        word = DBAddUser(user)
        connection.commit()
        connection.close()
        return word
    else:
        word = randint(0, 454)
        cursor.execute('UPDATE hooy SET CurrentWord = ? WHERE User = ?', (word, user))
        connection.commit()
        connection.close()
        return word

def DBWordCheck(user, word):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    cursor.execute('SELECT CurrentWord FROM hooy WHERE User = ?', (user,))
    a = cursor.fetchone()
    if a is None:
        return 2
    elif word == config.listof_correctwords[a[0]]:
        return 1
    else:
        return a[0]
    connection.commit()
    connection.close()

def DBWhichWord(user):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    cursor.execute('SELECT CurrentWord FROM hooy WHERE User = ?', (user,))
    a = cursor.fetchone()
    if a is None:
        a = DBAddUser(user)
    else:
        a = a[0]
    connection.commit()
    connection.close()
    return a

def DBAddToCounter(user, wol):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    if wol:
        cursor.execute('SELECT Wins FROM hooy WHERE User = ?', (user,))
        a = int(cursor.fetchone()[0]) + 1
        cursor.execute('UPDATE hooy SET Wins = ? WHERE User = ?', (a, user))
    else:
        cursor.execute('SELECT Loses FROM hooy WHERE User = ?', (user,))
        a = int(cursor.fetchone()[0]) + 1
        cursor.execute('UPDATE hooy SET Loses = ? WHERE User = ?', (a, user))
    connection.commit()
    connection.close()

def DBCounter(user):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    cursor.execute('SELECT Wins FROM hooy WHERE User = ?', (user,))
    wins = cursor.fetchone()[0]
    cursor.execute('SELECT Loses FROM hooy WHERE User = ?', (user,))
    loses = cursor.fetchone()[0]
    connection.commit()
    connection.close()
    a = 'Wins/Loses:\r\n' + str(wins) + '/' + str(loses)
    return a

def DBLastMID(user):
    connection = sqlite3.connect('currentwords.db')
    cursor = connection.cursor()
    cursor.execute('SELECT LastMID FROM hooy WHERE User = ?', (user,))
    lmid = cursor.fetchone()[0]
    return lmid


def WordSplit(word, chatid):

    a = 0
    buttonlist = []
    cbbuttonlist = []
    cword = config.listof_testwords[word]
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for i in range(len(cword)):
        if cword[i] in config.galphabet:
            if i+1 < len(cword):
                buttonlist.append(cword[:i] + cword[i].upper() + cword[i+1:])
            else:
                buttonlist.append(cword[:i] + cword[i].upper())
    for i in buttonlist:
        if a == 0:
            callback_button0 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 1:
            callback_button1 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 2:
            callback_button2 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 3:
            callback_button3 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 4:
            callback_button4 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 5:
            callback_button5 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 6:
            callback_button6 = types.InlineKeyboardButton(text=i, callback_data=i)
        elif a == 7:
            callback_button7 = types.InlineKeyboardButton(text=i, callback_data=i)
        a += 1
#        cbbuttonlist.append(callback_button)
#        keyboard.add(callback_button)
    a -= 1
    if a == 0:
        keyboard.add(callback_button0)
    elif a == 1:
        keyboard.add(callback_button0, callback_button1)
    elif a == 2:
        keyboard.add(callback_button0, callback_button1, callback_button2)
    elif a == 3:
        keyboard.add(callback_button0, callback_button1, callback_button2, callback_button3)
    elif a == 4:
        keyboard.add(callback_button0, callback_button1, callback_button2, callback_button3, callback_button4)
    elif a == 5:
        keyboard.add(callback_button0, callback_button1, callback_button2, callback_button3, callback_button4, callback_button5)
    elif a == 6:
        keyboard.add(callback_button0, callback_button1, callback_button2, callback_button3, callback_button4, callback_button5, callback_button6)
    elif a == 7:
        keyboard.add(callback_button0, callback_button1, callback_button2, callback_button3, callback_button4, callback_button5, callback_button6, callback_button7)
    bot.send_message(chatid, cword, reply_markup=keyboard)
    return

bot.polling(none_stop=True)