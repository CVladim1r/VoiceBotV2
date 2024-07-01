import os
import telebot
from telebot import types
import whisper
import pyttsx3
from deep_translator import GoogleTranslator
import threading

TOKEN = "7333829099:AAEEZwRKGH7Ox-Vk0xELgVEWRV61mhcrog4"
bot = telebot.TeleBot(TOKEN)

user_status = {}
synthesizer = pyttsx3.init()

@bot.message_handler(commands=["start"])
def start_message(message: types.Message):
    bot.send_message(message.chat.id, 'Отправьте голосовое сообщение')
    
    if not os.path.exists("voice_messages"):
        os.makedirs("voice_messages")
    if not os.path.exists("synthesized_messages"):
        os.makedirs("synthesized_messages")

@bot.message_handler(content_types=['voice'])
def voice_processing(message: types.Message):
    threading.Thread(target=process_voice, args=(message,)).start()

def process_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(f'{message.from_user.id}_rawVoice.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    user_status[message.chat.id] = 'waiting_transcript'

@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'waiting_transcript')
def handle_transcript_request(message: types.Message):
    threading.Thread(target=process_transcript, args=(message,)).start()

def process_transcript(message):
    model = whisper.load_model("small")
    result = model.transcribe(f"{message.from_user.id}_rawVoice.ogg")
    transcript = result['text']
    bot.send_message(message.chat.id, f'{transcript}')
    user_status[message.chat.id] = {'transcript': transcript, 'language': None, 'translated_text': None}

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text.startswith("Перевести на"))
def handle_translation_choice(message: types.Message):
    threading.Thread(target=process_translation, args=(message,)).start()

def process_translation(message):
    user_data = user_status[message.chat.id]
    transcript = user_data['transcript']
    translated_text = ""
    if message.text == "Перевести на английский":
        translated_text = GoogleTranslator(source='auto', target='en').translate(transcript)
        user_data['language'] = 'en'
    elif message.text == "Перевести на испанский":
        translated_text = GoogleTranslator(source='auto', target='es').translate(transcript)
        user_data['language'] = 'es'
    elif message.text == "Перевести на итальянский":
        translated_text = GoogleTranslator(source='auto', target='it').translate(transcript)
        user_data['language'] = 'it'
    elif message.text == "Перевести на русский":
        translated_text = GoogleTranslator(source='auto', target='ru').translate(transcript)
        user_data['language'] = 'ru'

    user_data['translated_text'] = translated_text

    markup = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, f"Перевод:\n{user_data['translated_text']}", reply_markup=markup)

    markup_actions = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton("Выбрать другой перевод")
    button_synthesize = types.KeyboardButton("Синтезировать голос")
    markup_actions.add(button_back, button_synthesize)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup_actions)

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Синтезировать голос")
def handle_synthesize_button(message: types.Message):
    threading.Thread(target=process_synthesize, args=(message,)).start()

def process_synthesize(message):
    markup_actions = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Ожидайте")
    bot.send_message(message.chat.id, "Синтезирование выполняется...", reply_markup=markup_actions)

    user_data = user_status[message.chat.id]
    translated_text = user_data['translated_text']
    synthesizer.save_to_file(translated_text, f'synthesized_messages/{message.chat.id}_synthesized.ogg')
    synthesizer.runAndWait()

    with open(f'synthesized_messages/{message.chat.id}_synthesized.ogg', 'rb') as audio:
        bot.send_audio(message.chat.id, audio, caption=user_data['translated_text'])

    os.remove(f'synthesized_messages/{message.chat.id}_synthesized.ogg')
    user_status[message.chat.id] = None

    bot.send_message(message.chat.id, "Для продолжения отправьте новое голосовое или перешлите предыдущее")

@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Выбрать другой перевод")
def handle_back_button(message: types.Message):
    markup_translate = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_english = types.KeyboardButton("Перевести на английский")
    button_spanish = types.KeyboardButton("Перевести на испанский")
    button_italian = types.KeyboardButton("Перевести на итальянский")
    button_russian = types.KeyboardButton("Перевести на русский")
    markup_translate.add(button_english, button_spanish, button_italian, button_russian)

    bot.send_message(message.chat.id, "Выберите язык для перевода:", reply_markup=markup_translate)

    user_data = user_status[message.chat.id]
    user_data['language'] = None

@bot.inline_handler(lambda query: query.query.startswith('translate'))
def handle_inline_query(query):
    results = []
    replied_message = query.from_user.reply_to_message

    if replied_message and replied_message.voice:
        voice_message = replied_message.voice
        file_info = bot.get_file(voice_message.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        voice_file_path = f'voice_{voice_message.file_id}.ogg'
        
        with open(voice_file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        try:
            translated_text_en = GoogleTranslator(source='auto', target='en').translate_voice(voice_file_path)
            translated_text_es = GoogleTranslator(source='auto', target='es').translate_voice(voice_file_path)
            translated_text_it = GoogleTranslator(source='auto', target='it').translate_voice(voice_file_path)
            translated_text_ru = GoogleTranslator(source='auto', target='ru').translate_voice(voice_file_path)

            result_en = types.InlineQueryResultArticle(
                id='1', title='Английский',
                description=f'Перевод на английский: {translated_text_en}',
                input_message_content=types.InputTextMessageContent(message_text=f'Перевод на английский:\n{translated_text_en}')
            )

            result_es = types.InlineQueryResultArticle(
                id='2', title='Испанский',
                description=f'Перевод на испанский: {translated_text_es}',
                input_message_content=types.InputTextMessageContent(message_text=f'Перевод на испанский:\n{translated_text_es}')
            )

            result_it = types.InlineQueryResultArticle(
                id='3', title='Итальянский',
                description=f'Перевод на итальянский: {translated_text_it}',
                input_message_content=types.InputTextMessageContent(message_text=f'Перевод на итальянский:\n{translated_text_it}')
            )

            result_ru = types.InlineQueryResultArticle(
                id='4', title='Русский',
                description=f'Перевод на русский: {translated_text_ru}',
                input_message_content=types.InputTextMessageContent(message_text=f'Перевод на русский:\n{translated_text_ru}')
            )

            results.extend([result_en, result_es, result_it, result_ru])

        except Exception as e:
            print(f"Error handling inline query: {e}")

        finally:
            if os.path.exists(voice_file_path):
                os.remove(voice_file_path)

    bot.answer_inline_query(query.id, results)

@bot.message_handler(content_types=['voice'], func=lambda message: message.chat.type == 'group')
def handle_group_voice_message(message):
    threading.Thread(target=process_group_voice, args=(message,)).start()

def process_group_voice(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    voice_file_path = f'{message.chat.id}_{message.voice.file_id}.ogg'
    
    with open(voice_file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate_voice(voice_file_path)
        bot.send_message(message.chat.id, f'{translated_text}')
    
    except Exception as e:
        print(f"Error translating voice message: {e}")
    
    finally:
        if os.path.exists(voice_file_path):
            os.remove(voice_file_path)

import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

bot.polling()
