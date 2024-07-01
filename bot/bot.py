import os
import telebot
from telebot import types
import threading
import logging
import pyttsx3

from handlers import start_handler, voice_handler, transcript_handler, translation_handler, synthesis_handler, inline_handler, group_handler

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = telebot.TeleBot(TOKEN)

# Настройка логирования
logging.basicConfig(filename='logs/errors.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.ERROR)

user_status = {}
synthesizer = pyttsx3.init()

@bot.message_handler(commands=["start"])
def start_message(message: types.Message):
    try:
        start_handler.handle_start_message(bot, message, user_status)
    except Exception as e:
        logging.error(f"Error handling start command: {e}")

@bot.message_handler(content_types=['voice'])
def voice_processing(message: types.Message):
    try:
        threading.Thread(target=voice_handler.process_voice, args=(bot, message, user_status)).start()
    except Exception as e:
        logging.error(f"Error processing voice message: {e}")

@bot.message_handler(content_types=['voice', 'forwarded'])
def forwarded_voice_processing(message: types.Message):
    try:
        threading.Thread(target=voice_handler.process_voice, args=(bot, message, user_status)).start()
    except Exception as e:
        logging.error(f"Error processing forwarded voice message: {e}")

@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'waiting_transcript')
def handle_transcript_request(message: types.Message):
    try:
        threading.Thread(target=transcript_handler.process_transcript, args=(bot, message, user_status)).start()
    except Exception as e:
        logging.error(f"Error handling transcript request: {e}")

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text.startswith("Перевести на"))
def handle_translation_choice(message: types.Message):
    try:
        threading.Thread(target=translation_handler.process_translation, args=(bot, message, user_status)).start()
    except Exception as e:
        logging.error(f"Error handling translation choice: {e}")

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Синтезировать голос")
def handle_synthesize_button(message: types.Message):
    try:
        threading.Thread(target=synthesis_handler.process_synthesize, args=(bot, message, user_status, synthesizer)).start()
    except Exception as e:
        logging.error(f"Error handling synthesize button: {e}")

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Выбрать другой перевод")
def handle_back_button(message: types.Message):
    try:
        translation_handler.handle_back_button(bot, message, user_status)
    except Exception as e:
        logging.error(f"Error handling back button: {e}")

@bot.inline_handler(lambda query: query.query.startswith('translate'))
def inline_query_handler(query):
    try:
        threading.Thread(target=inline_handler.handle_inline_query, args=(bot, query)).start()
    except Exception as e:
        logging.error(f"Error handling inline query: {e}")

@bot.message_handler(content_types=['voice'], func=lambda message: message.chat.type == 'group')
def handle_group_voice_message(message: types.Message):
    try:
        threading.Thread(target=group_handler.handle_group_voice_message, args=(bot, message)).start()
    except Exception as e:
        logging.error(f"Error handling group voice message: {e}")

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

bot.polling()
