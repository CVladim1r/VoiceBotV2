import whisper
import logging
from ..utils.audio_processing import delete_audio, save_audio

# Настройка логирования
logging.basicConfig(filename='voicebot.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')

def process_transcript(bot, message, user_status):
    try:
        logging.info('Начало загрузки модели Whisper.')
        model = whisper.load_model("small")
        logging.info('Модель Whisper загружена успешно.')

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"{message.from_user.id}_rawVoice.ogg"
        
        # Save and process the voice file
        save_audio(file_path, downloaded_file)
        
        logging.info(f'Начало транскрипции файла: {file_path}')
        result = model.transcribe(file_path)
        transcript = result['text']
        
        logging.info(f'Транскрипция завершена: {transcript}')
        
        # Send the transcript to the user
        bot.send_message(message.chat.id, transcript)
        logging.info(f'Отправлено сообщение с транскрипцией: {transcript}')
        
        # Update user status
        user_status[message.chat.id] = {'transcript': transcript, 'language': None, 'translated_text': None}
        
        # Delete the audio file
        delete_audio(file_path)
        logging.info(f'Аудиофайл {file_path} удален.')
    
    except Exception as e:
        error_message = f'Ошибка при обработке транскрипции: {str(e)}'
        print(error_message)
        logging.error(error_message)
        
        # Send error message to user
        bot.send_message(message.chat.id, 'Произошла ошибка при обработке вашего голосового сообщения. Попробуйте еще раз.')
