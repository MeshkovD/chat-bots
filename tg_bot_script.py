import logging
import os
from time import sleep

import requests
import telegram
from dotenv import load_dotenv


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main():
    load_dotenv()

    DEVMAN_AUTH_TOKEN = os.getenv('DEVMAN_AUTH_TOKEN')
    TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
    TG_CHAT_ID = os.getenv('TG_CHAT_ID')

    url = 'https://dvmn.org/api/long_polling'
    headers = {'Authorization': DEVMAN_AUTH_TOKEN}

    tg_bot = telegram.Bot(token=TG_BOT_TOKEN)

    logger = logging.getLogger('Logger')
    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogsHandler(tg_bot, TG_CHAT_ID))
    logger.info('Бот запущен')

    payload = None

    while True:
        try:
            response = requests.get(url, headers=headers, data=payload, timeout=120)
            response.raise_for_status()
            review_info = response.json()
            payload = {'timestamp': review_info.get('timestamp_to_request')}

            if review_info.get('status') == "found":
                new_attempt = review_info.get('new_attempts')[0]

                lesson_title = new_attempt.get('lesson_title')
                lesson_url = new_attempt.get('lesson_url')
                is_negative = new_attempt.get('is_negative')

                checking_result = 'Есть ошибки' if is_negative else 'Работа прошла проверку'

                message = f'''Работа "{lesson_title}" проверена \n{checking_result} \nСсылка на урок: {lesson_url}'''

                tg_bot.send_message(chat_id=TG_CHAT_ID, text=message)

        except requests.exceptions.ConnectTimeout as error:
            logger.critical(f'Ошибка: \n{error}', exc_info=True)

        except requests.exceptions.ReadTimeout as error:
            logger.error(f'Ошибка: \n{error}', exc_info=True)

        except requests.exceptions.ConnectionError as error:
            logger.error(f'Ошибка: \n{error}', exc_info=True)
            sleep(30)


if __name__ == '__main__':
    main()
