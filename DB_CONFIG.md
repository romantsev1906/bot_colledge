# Инструкция по настройке подключения к удаленной БД

## Как заставить работать бот и мини-приложение с одной БД

### Вариант 1: PostgreSQL на удаленном сервере (рекомендуется)

#### Шаг 1: Настройка web_app.py

В файле `web_app.py` найдите секцию `DB_CONFIG` и измените:

```python
DB_CONFIG = {
    'type': 'postgresql',
    'host': 'your-server.com',  # IP или домен сервера
    'port': 5432,
    'database': 'students_db',   # Имя БД
    'user': 'your_user',         # Пользователь БД
    'password': 'your_password'   # Пароль
}
```

Раскомментируйте код в функции `get_db_connection()`:

```python
def get_db_connection():
    if DB_CONFIG['type'] == 'postgresql':
        import psycopg2
        return psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
```

#### Шаг 2: Настройка bot_main.py

В файле `bot_main.py` замените:

```python
conn = sqlite3.connect("students.db", check_same_thread=False)
```

На:

```python
import psycopg2
conn = psycopg2.connect(
    host='your-server.com',
    port=5432,
    database='students_db',
    user='your_user',
    password='your_password'
)
```

**Важно:** Для PostgreSQL нужно изменить синтаксис SQL запросов:
- `?` заменяется на `%s`
- `AUTOINCREMENT` заменяется на `SERIAL`
- `INTEGER PRIMARY KEY` заменяется на `SERIAL PRIMARY KEY`

#### Шаг 3: Установка зависимостей

```bash
pip install psycopg2-binary
```

### Вариант 2: MySQL на удаленном сервере

#### Шаг 1: Настройка web_app.py

```python
DB_CONFIG = {
    'type': 'mysql',
    'host': 'your-server.com',
    'port': 3306,
    'database': 'students_db',
    'user': 'your_user',
    'password': 'your_password'
}
```

Раскомментируйте код для MySQL в `get_db_connection()`:

```python
elif DB_CONFIG['type'] == 'mysql':
    import pymysql
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG.get('port', 3306),
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
```

#### Шаг 2: Настройка bot_main.py

```python
import pymysql
conn = pymysql.connect(
    host='your-server.com',
    port=3306,
    database='students_db',
    user='your_user',
    password='your_password'
)
```

**Важно:** Для MySQL также нужно изменить синтаксис:
- `?` заменяется на `%s`
- `AUTOINCREMENT` заменяется на `AUTO_INCREMENT`
- Типы данных могут отличаться

#### Шаг 3: Установка зависимостей

```bash
pip install PyMySQL
```

### Вариант 3: SQLite с синхронизацией

Если нужно оставить SQLite, но синхронизировать данные:

1. Создайте скрипт синхронизации, который периодически копирует данные
2. Используйте общую сетевую папку для SQLite файла
3. Или используйте SQLite с репликацией

### Миграция данных из SQLite в PostgreSQL/MySQL

#### Шаг 1: Экспорт из SQLite

```python
import sqlite3
import json

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

# Экспортируйте данные из каждой таблицы
tables = ['users', 'students', 'teachers', 'disciplines', 'grades', 'ktp', ...]
data = {}
for table in tables:
    cursor.execute(f"SELECT * FROM {table}")
    data[table] = cursor.fetchall()
    
with open('data_export.json', 'w') as f:
    json.dump(data, f)
```

#### Шаг 2: Импорт в PostgreSQL/MySQL

```python
import psycopg2
import json

conn = psycopg2.connect(...)
cursor = conn.cursor()

with open('data_export.json', 'r') as f:
    data = json.load(f)
    
# Импортируйте данные в соответствующие таблицы
for table, rows in data.items():
    for row in rows:
        # Вставка данных
        pass
```

### Проверка подключения

Создайте тестовый скрипт `test_db.py`:

```python
import psycopg2  # или pymysql

try:
    conn = psycopg2.connect(
        host='your-server.com',
        port=5432,
        database='students_db',
        user='your_user',
        password='your_password'
    )
    print("Подключение успешно!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    print(cursor.fetchone())
    conn.close()
except Exception as e:
    print(f"Ошибка подключения: {e}")
```

### Безопасность

1. **Используйте переменные окружения для паролей:**

```python
import os

DB_CONFIG = {
    'type': 'postgresql',
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'students_db'),
    'user': os.getenv('DB_USER', 'user'),
    'password': os.getenv('DB_PASSWORD', 'password')
}
```

2. **Ограничьте доступ к БД по IP**
3. **Используйте SSL для подключения:**

```python
conn = psycopg2.connect(
    ...,
    sslmode='require'
)
```

### Решение проблем

**Ошибка: "connection refused"**
- Проверьте, что сервер БД запущен
- Проверьте firewall настройки
- Убедитесь, что порт открыт

**Ошибка: "authentication failed"**
- Проверьте логин и пароль
- Проверьте права пользователя БД

**Ошибка: "database does not exist"**
- Создайте БД на сервере
- Проверьте имя БД в конфигурации

**Ошибка синтаксиса SQL**
- Убедитесь, что используете правильные плейсхолдеры (`%s` для PostgreSQL/MySQL)
- Проверьте совместимость типов данных

