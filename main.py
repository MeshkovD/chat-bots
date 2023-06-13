import os
from time import sleep

import requests
from dotenv import load_dotenv
import telegram


load_dotenv()

DEVMAN_AUTH_TOKEN = os.getenv('DEVMAN_AUTH_TOKEN')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
TG_CHAT_ID = os.getenv('TG_CHAT_ID')

url = 'https://dvmn.org/api/long_polling'
headers = {'Authorization': DEVMAN_AUTH_TOKEN}
payload = None

bot = telegram.Bot(token=TG_BOT_TOKEN)

while True:
    try:
        response = requests.get(url, headers=headers, data=payload, timeout=120)
        response.raise_for_status()
        payload = {'timestamp': response.json().get('timestamp_to_request')}

        if response.json().get('status') == "found":
            try:
                new_attempts = response.json().get('new_attempts')[0]
            except IndexError as error:
                print('IndexError')
                continue

            lesson_title = new_attempts.get('lesson_title')
            lesson_url = new_attempts.get('lesson_url')
            is_negative = new_attempts.get('is_negative')

            checking_result = 'Есть ошибки' if is_negative else 'Работа прошла проверку'

            message = f"У вас проверили работу '{lesson_title}'\n" \
                      f"{checking_result}\n" \
                      f"Ссылка на урок: {lesson_url}"
            bot.send_message(chat_id=TG_CHAT_ID, text=message)

    except requests.exceptions.ConnectTimeout as error:
        print('ConnectTimeout')

    except requests.exceptions.ReadTimeout as error:
        print('ReadTimeout')

    except requests.exceptions.ConnectionError as e:
        print(f'Error connecting to server: {e}')
        sleep(30)