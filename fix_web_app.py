"""
Скрипт для быстрого исправления web_app.py
Заменяет все использования get_db_connection/get_cursor на заглушки
"""
import re

with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Добавляем заглушки для функций, которые еще используются
stub_functions = '''
def get_db_connection():
    """Заглушка - функция не используется, данные получаются через API"""
    raise NotImplementedError("Используйте api_request() вместо прямого подключения к БД")

def get_cursor(conn):
    """Заглушка - функция не используется"""
    raise NotImplementedError("Используйте api_request() вместо прямого подключения к БД")
'''

# Вставляем заглушки после api_request
if 'def api_request' in content and 'def get_db_connection' not in content:
    content = content.replace(
        'def api_request(method, endpoint, data=None, params=None):',
        stub_functions + '\n\ndef api_request(method, endpoint, data=None, params=None):'
    )
    
    with open('web_app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Добавлены заглушки для get_db_connection и get_cursor")
    print("ВНИМАНИЕ: Функции, использующие эти методы, нужно переделать на api_request()")
else:
    print("Файл уже исправлен или структура изменилась")


