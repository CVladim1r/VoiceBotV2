from ..utils.audio_processing import save_audio, delete_audio
from ..utils.translator import translate_text

def handle_group_voice_message(bot, message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    voice_file_path = f'{message.chat.id}_{message.voice.file_id}.ogg'
    
    save_audio(voice_file_path, downloaded_file)
    
    try:
        translated_text = translate_text(voice_file_path, 'en')
        
        if message.reply_to_message:
            bot.reply_to(message.reply_to_message, f'{translated_text}')
        else:
            bot.reply_to(message, f'{translated_text}')
    
    except Exception as e:
        print(f"Error translating voice message: {e}")
    
    finally:
        delete_audio(voice_file_path)
