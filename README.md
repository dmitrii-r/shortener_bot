# shortener_bot

Стек:  Python3, aiogram, PostgreSQL

## Возможности бота:
1. Принимать ссылки, выдавать сокращенные.
2. Выводить список ссылок со статистикой, сколько раз она была использована.

## Запуск бота на локальном хранилище

Клонируйте репозиторий и перейдите в него:
```
git clone https://github.com/dmitrii-r/shortener_bot.git
```
```
cd shortener_bot
```
Cоздайте и активируйте виртуальное окружение:
```
python3 -m venv env
```
```
source env/bin/activate
```
Обновите установщик пакетов PIP:
```
python3 -m pip install --upgrade pip
```
Установите зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```
Создайте файл .env и заполните его по образцу .env.example.

Убедитесь, что у вас запущен сервер PostgreSQL и на нем создана соответствующая база данных.

Запустите исполняемый файл бота:
```
python3 bot.py
```
