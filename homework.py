import os
import time

from dotenv import load_dotenv
import requests
from requests.exceptions import (
    ConnectionError, Timeout, RequestException,
    InvalidHeader, InvalidURL, ProxyError, InvalidProxyURL
    )
import telegram

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

proxy = telegram.utils.request.Request(
    proxy_url='socks5://95.110.194.245:26518'
    )

bot = telegram.Bot(token=TELEGRAM_TOKEN, request=proxy)


def parse_homework_status(homework):
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    else:
        verdict = (
            'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
            )
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    url = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    data = {
        'from_date': current_timestamp,
    }
    try:
        homework_statuses = requests.get(url, params=data, headers=headers)
        return homework_statuses.json()
    except ProxyError:
        print("Ошибка прокси-сервера!")
        return {}
    except ConnectionError:
        print("Возникла ошибка соединения! Проверьте Ваше подключение к интернету.")
        return {}
    except Timeout:
        print("Время ожидания запроса истекло!")
        return {}
    except InvalidProxyURL:
        print("Недопустимый URL-адрес прокси-сервера!")
        return {}
    except InvalidURL:
        print("Недействительный URL-адрес!")
        return {}
    except InvalidHeader:
        print("Недопустимое значение заголовка!")
        return {}
    except RequestException:
        print("Что-то пошло не так...")
        return {}


def send_message(message):
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            homeworks = new_homework.get('homeworks', [])
            if homeworks:
                send_message(parse_homework_status(homeworks[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(1200)  # опрашивать раз в 20 минут

        except KeyboardInterrupt:
            finish = input(
                'Вы действительно хотите прервать работу бота? Y/N: '
                )
            if finish in ('Y', 'y'):
                print('До встречи!')
                break
            elif finish in ('N', 'n'):
                print('Продолжаем работать!')

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
