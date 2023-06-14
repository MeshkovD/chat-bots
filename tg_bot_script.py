import os
from time import sleep

import requests
import telegram
from dotenv import load_dotenv


def main():
    load_dotenv()

    DEVMAN_AUTH_TOKEN = os.getenv('DEVMAN_AUTH_TOKEN')
    TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
    TG_CHAT_ID = os.getenv('TG_CHAT_ID')

    url = 'https://dvmn.org/api/long_polling'
    headers = {'Authorization': DEVMAN_AUTH_TOKEN}

    bot = telegram.Bot(token=TG_BOT_TOKEN)

    payload = None

    while True:
        try:
            response = requests.get(url, headers=headers, data=payload, timeout=120)
            response.raise_for_status()
            response_json = response.json()
            payload = {'timestamp': response_json.get('timestamp_to_request')}

            if response_json.get('status') == "found":
                if response_json.get('new_attempts'):
                    new_attempts = response_json.get('new_attempts')[0]
                else:
                    continue

                lesson_title = new_attempts.get('lesson_title')
                lesson_url = new_attempts.get('lesson_url')
                is_negative = new_attempts.get('is_negative')

                checking_result = 'Есть ошибки' if is_negative else 'Работа прошла проверку'

                message = f'''Работа "{lesson_title}" проверена \n{checking_result} \nСсылка на урок: {lesson_url}'''

                bot.send_message(chat_id=TG_CHAT_ID, text=message)

        except requests.exceptions.ConnectTimeout as error:
            print('ConnectTimeout')

        except requests.exceptions.ReadTimeout as error:
            print('ReadTimeout')

        except requests.exceptions.ConnectionError as e:
            print(f'Error connecting to server: {e}')
            sleep(30)


if __name__ == '__main__':
    main()
