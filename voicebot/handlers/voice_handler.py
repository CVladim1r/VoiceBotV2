from utils.audio_processing import save_audio

def process_voice(bot, message, user_status):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f'{message.from_user.id}_rawVoice.ogg'
    save_audio(file_path, downloaded_file)
    user_status[message.chat.id] = 'waiting_transcript'
