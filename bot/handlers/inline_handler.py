from telebot import types
from utils.audio_processing import save_audio, delete_audio
from utils.translator import translate_text

def handle_inline_query(bot, query):
    results = []
    replied_message = query.from_user.reply_to_message

    if replied_message and replied_message.voice:
        voice_message = replied_message.voice
        file_info = bot.get_file(voice_message.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        voice_file_path = f'voice_{voice_message.file_id}.ogg'
        
        save_audio(voice_file_path, downloaded_file)
        
        try:
            translated_text_en = translate_text(voice_file_path, 'en')
            translated_text_es = translate_text(voice_file_path, 'es')
            translated_text_it = translate_text(voice_file_path, 'it')
            translated_text_ru = translate_text(voice_file_path, 'ru')

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
            delete_audio(voice_file_path)

    bot.answer_inline_query(query.id, results)
