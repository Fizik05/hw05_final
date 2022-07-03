# Социальная сеть Yatube
## В этой социальной сети вы сможете публиковать свои посты, оставлять комментарии к другим постам и многое другое
____
## Развёртывание проекта
- Для того, чтобы развернуть этот проект у себя на ПК нужно открыть терминал и вбить команду ```git clone https://github.com/Fizik05/hw05_final.git```
- Далее устанавливаем виртуальное окружение в корневую папку проекта ```python -m venv venv```
- После активируем его ```source venv/Scripts/activate```, обновляем PIP ```python -m pip install --upgrade pip``` и устанавливаем зависимости ```pip install -r requirements.txt```
- После переходим в директорию yatube, используя команду ```cd yatube``` в терминале, проводим миграции ```python manage.py makemigrations``` -> ```python manage.py migrate``` и собираем статику ```python manage.py collectstatic```
- В конечном счёте поднимаем наш проект локально ```python manage.py runserver```
____
## Системные требования
- Python=3.7+
- PIP=22.0.4
____
