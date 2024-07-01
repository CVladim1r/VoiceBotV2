from telebot import types
from utils.translator import translate_text

def process_translation(bot, message, user_status):
    user_data = user_status[message.chat.id]
    transcript = user_data['transcript']
    translated_text = ""
    if message.text == "Перевести на английский":
        translated_text = translate_text(transcript, 'en')
        user_data['language'] = 'en'
    elif message.text == "Перевести на испанский":
        translated_text = translate_text(transcript, 'es')
        user_data['language'] = 'es'
    elif message.text == "Перевести на итальянский":
        translated_text = translate_text(transcript, 'it')
        user_data['language'] = 'it'
    elif message.text == "Перевести на русский":
        translated_text = translate_text(transcript, 'ru')
        user_data['language'] = 'ru'

    user_data['translated_text'] = translated_text

    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Перевод:\n{user_data['translated_text']}", reply_markup=markup)

    markup_actions = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("Выбрать другой перевод")
    button_synthesize = types.KeyboardButton("Синтезировать голос")
    markup_actions.add(button_back, button_synthesize)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup_actions)

def handle_back_button(bot, message, user_status):
    markup_translate = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_english = types.KeyboardButton("Перевести на английский")
    button_spanish = types.KeyboardButton("Перевести на испанский")
    button_italian = types.KeyboardButton("Перевести на итальянский")
    button_russian = types.KeyboardButton("Перевести на русский")
    markup_translate.add(button_english, button_spanish, button_italian, button_russian)

    bot.send_message(message.chat.id, "Выберите язык для перевода:", reply_markup=markup_translate)

    user_data = user_status[message.chat.id]
    user_data['language'] = None
