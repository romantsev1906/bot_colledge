"""
Быстрый тест запуска сайта
"""
import sys
import os

print("Проверка импорта...")
try:
    from web_app import app
    print("✓ Импорт успешен")
except Exception as e:
    print(f"✗ Ошибка импорта: {e}")
    sys.exit(1)

print("\nПроверка маршрутов...")
with app.test_client() as client:
    try:
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Главная страница работает")
        else:
            print(f"⚠ Главная страница вернула код: {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка при запросе главной страницы: {e}")

print("\nПроверка статических файлов...")
static_path = os.path.join(os.path.dirname(__file__), 'static')
if os.path.exists(static_path):
    print(f"✓ Папка static существует: {static_path}")
else:
    print(f"⚠ Папка static не найдена: {static_path}")

templates_path = os.path.join(os.path.dirname(__file__), 'templates')
if os.path.exists(templates_path):
    print(f"✓ Папка templates существует: {templates_path}")
else:
    print(f"✗ Папка templates не найдена: {templates_path}")

print("\nПроверка API_CONFIG...")
try:
    from web_app import API_CONFIG
    print(f"API URL: {API_CONFIG['base_url']}")
    if 'your-bot-server.com' in API_CONFIG['base_url']:
        print("⚠ ВНИМАНИЕ: API_CONFIG не настроен! Обновите base_url в web_app.py")
    else:
        print("✓ API_CONFIG настроен")
except Exception as e:
    print(f"✗ Ошибка: {e}")

print("\n" + "="*50)
print("Для запуска сайта выполните: python web_app.py")
print("Затем откройте: http://localhost:5000")


