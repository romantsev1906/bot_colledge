"""
Тестовый скрипт для проверки подключения к MySQL
"""
import pymysql

DB_CONFIG = {
    'host': 'sql313.infinityfree.com',
    'port': 3306,
    'database': 'if0_40442945_students',  # Убрал .db - в MySQL имена БД без расширения
    'user': 'if0_40442945',
    'password': 'Asdf55520071'
}

try:
    print("Попытка подключения к MySQL...")
    conn = pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        database=DB_CONFIG['database'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✓ Подключение успешно!")
    
    cursor = conn.cursor()
    
    # Проверяем версию MySQL
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"✓ Версия MySQL: {version['VERSION()']}")
    
    # Показываем список таблиц
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"\n✓ Найдено таблиц: {len(tables)}")
    for table in tables:
        table_name = list(table.values())[0]
        print(f"  - {table_name}")
    
    # Проверяем таблицу users
    try:
        cursor.execute("SELECT COUNT(*) as count FROM users")
        users_count = cursor.fetchone()
        print(f"\n✓ Пользователей в БД: {users_count['count']}")
    except Exception as e:
        print(f"\n⚠ Таблица 'users' не найдена или ошибка: {e}")
        print("  Возможно, нужно создать таблицы из bot_main.py")
    
    conn.close()
    print("\n✓ Тест завершен успешно!")
    
except pymysql.Error as e:
    print(f"✗ Ошибка подключения к MySQL: {e}")
    print("\nВозможные причины:")
    print("1. Неправильное имя базы данных (замените XXX на реальное имя)")
    print("2. Сервер недоступен")
    print("3. Неправильные учетные данные")
    print("4. Firewall блокирует подключение")
except Exception as e:
    print(f"✗ Неожиданная ошибка: {e}")

