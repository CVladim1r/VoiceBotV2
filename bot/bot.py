import os
import telebot
from telebot import types
import threading
import pyttsx3

from handlers import start_handler, voice_handler, transcript_handler, translation_handler, synthesis_handler, inline_handler, group_handler

TOKEN = "7333829099:AAEB-c4gVL0qYJ94qN_mtmGQ2q4fOH0hoSk"
bot = telebot.TeleBot(TOKEN)

user_status = {}
synthesizer = pyttsx3.init()

@bot.message_handler(commands=["start"])
def start_message(message: types.Message):
    start_handler.handle_start_message(bot, message, user_status)

@bot.message_handler(content_types=['voice'])
def voice_processing(message: types.Message):
    threading.Thread(target=voice_handler.process_voice, args=(bot, message, user_status)).start()

@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'waiting_transcript')
def handle_transcript_request(message: types.Message):
    threading.Thread(target=transcript_handler.process_transcript, args=(bot, message, user_status)).start()

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text.startswith("Перевести на"))
def handle_translation_choice(message: types.Message):
    threading.Thread(target=translation_handler.process_translation, args=(bot, message, user_status)).start()

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Синтезировать голос")
def handle_synthesize_button(message: types.Message):
    threading.Thread(target=synthesis_handler.process_synthesize, args=(bot, message, user_status, synthesizer)).start()

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Выбрать другой перевод")
def handle_back_button(message: types.Message):
    translation_handler.handle_back_button(bot, message, user_status)

@bot.inline_handler(lambda query: query.query.startswith('translate'))
def inline_query_handler(query):
    threading.Thread(target=inline_handler.handle_inline_query, args=(bot, query)).start()

@bot.message_handler(content_types=['voice'], func=lambda message: message.chat.type == 'group')
def handle_group_voice_message(message: types.Message):
    threading.Thread(target=group_handler.handle_group_voice_message, args=(bot, message)).start()

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

bot.polling()
