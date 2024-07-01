from telebot import types
from utils.synthesizer import synthesize_text, delete_synthesized_audio

def process_synthesize(bot, message, user_status, synthesizer):
    markup_actions = types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Ожидайте")
    bot.send_message(message.chat.id, "Синтезирование выполняется...", reply_markup=markup_actions)

    user_data = user_status[message.chat.id]
    translated_text = user_data['translated_text']
    output_path = f'synthesized_messages/{message.chat.id}_synthesized.ogg'
    synthesize_text(translated_text, output_path)

    with open(output_path, 'rb') as audio:
        bot.send_audio(message.chat.id, audio, caption=user_data['translated_text'])

    delete_synthesized_audio(output_path)
    user_status[message.chat.id] = None

    bot.send_message(message.chat.id, "Для продолжения отправьте новое голосовое или перешлите предыдущее")
