import os
import telebot
from telebot import types
import whisper
import pyttsx3
from deep_translator import GoogleTranslator

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
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    voice_file_path = f'{message.from_user.id}_rawVoice.ogg'
    
    with open(voice_file_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    
    if os.path.exists(voice_file_path):
        user_status[message.chat.id] = 'waiting_transcript'
    else:
        bot.send_message(message.chat.id, 'Ошибка при сохранении файла.')


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'waiting_transcript')
def handle_transcript_request(message: types.Message):
    voice_file_path = f"{message.from_user.id}_rawVoice.ogg"
    
    if not os.path.exists(voice_file_path):
        bot.send_message(message.chat.id, 'Аудиофайл не найден.')
        return
    
    model = whisper.load_model("small")  # using the smaller model for faster performance
    
    try:
        result = model.transcribe(voice_file_path)
        transcript = result['text']
        bot.send_message(message.chat.id, f'{transcript}')
        user_status[message.chat.id] = {'transcript': transcript, 'language': None, 'translated_text': None}
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при транскрипции: {str(e)}')
        user_status[message.chat.id] = None


@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Перевести на английский")
def handle_translation_choice_english(message: types.Message):
    handle_translation(message, 'en')


@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Перевести на испанский")
def handle_translation_choice_spanish(message: types.Message):
    handle_translation(message, 'es')


@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Перевести на итальянский")
def handle_translation_choice_italian(message: types.Message):
    handle_translation(message, 'it')


@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Перевести на русский")
def handle_translation_choice_russian(message: types.Message):
    handle_translation(message, 'ru')


def handle_translation(message: types.Message, target_lang: str):
    user_data = user_status[message.chat.id]
    transcript = user_data['transcript']
    
    try:
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(transcript)
        user_data['language'] = target_lang
        user_data['translated_text'] = translated_text

        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, f"Перевод:\n{user_data['translated_text']}", reply_markup=markup)

        markup_actions = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_back = types.KeyboardButton("Выбрать другой перевод")
        button_synthesize = types.KeyboardButton("Синтезировать голос")
        markup_actions.add(button_back, button_synthesize)

        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup_actions)
    except Exception as e:
        bot.send_message(message.chat.id, f'Ошибка при переводе: {str(e)}')


@bot.message_handler(func=lambda message: isinstance(user_status.get(message.chat.id), dict) and message.text == "Синтезировать голос")
def handle_synthesize_button(message: types.Message):
    markup_actions = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Ожидайте")
    bot.send_message(message.chat.id, "Синтезирование выполняется...", reply_markup=markup_actions)

    user_data = user_status[message.chat.id]
    translated_text = user_data['translated_text']
    
    audio_file_path = f'synthesized_messages/{message.chat.id}_synthesized.ogg'
    synthesizer.save_to_file(translated_text, audio_file_path)
    synthesizer.runAndWait()

    if os.path.exists(audio_file_path):
        with open(audio_file_path, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, caption=user_data['translated_text'])
        os.remove(audio_file_path)
    else:
        bot.send_message(message.chat.id, "Ошибка при синтезировании аудио.")

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


import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

bot.polling()
