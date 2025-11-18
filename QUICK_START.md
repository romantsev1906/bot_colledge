# Быстрый старт

## 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 2. Настройка БД

### Для локальной SQLite (по умолчанию):
Ничего менять не нужно, используйте `students.db` из папки с ботом.

### Для удаленной PostgreSQL:
1. Откройте `web_app.py`
2. Измените `DB_CONFIG`:
```python
DB_CONFIG = {
    'type': 'postgresql',
    'host': 'your-server.com',
    'port': 5432,
    'database': 'students_db',
    'user': 'your_user',
    'password': 'your_password'
}
```
3. Раскомментируйте код PostgreSQL в функции `get_db_connection()`
4. Установите: `pip install psycopg2-binary`

### Для удаленной MySQL:
1. Откройте `web_app.py`
2. Измените `DB_CONFIG` аналогично PostgreSQL
3. Раскомментируйте код MySQL в функции `get_db_connection()`
4. Установите: `pip install PyMySQL`

## 3. Добавление логотипа

Поместите файл `logo.png` в папку `static/`

## 4. Запуск

```bash
python web_app.py
```

Откройте в браузере: `http://localhost:5000`

## 5. Настройка Telegram Mini App

1. Откройте @BotFather в Telegram
2. Выберите вашего бота
3. Используйте команду `/newapp`
4. Укажите URL вашего веб-приложения (например: `https://your-domain.com`)

## Важные замечания

- Для работы в Telegram Mini App требуется HTTPS
- Убедитесь, что БД доступна с сервера, где запущено приложение
- Проверьте права доступа к файлам и папкам

## Синхронизация с ботом

Если бот и веб-приложение должны работать с одной БД:

1. Настройте подключение к удаленной БД в обоих файлах (`bot_main.py` и `web_app.py`)
2. Убедитесь, что используются одинаковые настройки подключения
3. См. подробную инструкцию в `DB_CONFIG.md`

