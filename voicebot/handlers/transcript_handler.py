import whisper
from utils.audio_processing import delete_audio

def process_transcript(bot, message, user_status):
    model = whisper.load_model("small")
    file_path = f"{message.from_user.id}_rawVoice.ogg"
    result = model.transcribe(file_path)
    transcript = result['text']
    bot.send_message(message.chat.id, f'{transcript}')
    user_status[message.chat.id] = {'transcript': transcript, 'language': None, 'translated_text': None}
    delete_audio(file_path)
