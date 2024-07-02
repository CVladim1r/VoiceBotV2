import logging
from voicebot.bot import bot  # Импорт вашего бота
import time
import threading

# Configure logging to both file and console
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s',
    handlers=[
        logging.FileHandler('voicebot.log'),
        logging.StreamHandler()
    ]
)

def log_bot_status():
    while True:
        logging.info('Бот работает...')
        time.sleep(60)  # Log the status every 60 seconds

if __name__ == "__main__":
    try:
        print('Запуск бота')
        logging.info('Запуск бота.')
        
        # Start the thread for logging bot status
        status_thread = threading.Thread(target=log_bot_status)
        status_thread.daemon = True  # Daemonize thread to exit when the main program exits
        status_thread.start()
        
        bot.polling(none_stop=True)
    except Exception as e:
        print(f'Ошибка при запуске бота: {e}', flush=True)
        logging.error(f'Ошибка при запуске бота: {str(e)}')
