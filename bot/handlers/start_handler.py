import os

def handle_start_message(bot, message, user_status):
    bot.send_message(message.chat.id, 'Отправьте голосовое сообщение')
    
    if not os.path.exists("voice_messages"):
        os.makedirs("voice_messages")
    if not os.path.exists("synthesized_messages"):
        os.makedirs("synthesized_messages")
