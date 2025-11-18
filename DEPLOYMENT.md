# Инструкция по развертыванию на хостинге

## Подготовка к развертыванию

### 1. Обновите настройки для продакшена

Откройте `web_app.py` и измените:

```python
# В конце файла измените:
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)  # debug=False для продакшена
```

И настройте `API_CONFIG`:

```python
API_CONFIG = {
    'base_url': 'http://YOUR-BOT-SERVER-IP:5001',  # IP или домен сервера бота
}
```

### 2. Создайте файл `.env` для конфигурации (опционально)

Создайте файл `.env`:

```
API_BASE_URL=http://your-bot-server-ip:5001
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
```

И обновите `web_app.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_CONFIG = {
    'base_url': os.getenv('API_BASE_URL', 'http://localhost:5001'),
}

app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
```

Установите: `pip install python-dotenv`

## Варианты развертывания

### Вариант 1: Python хостинг (PythonAnywhere, Heroku, Railway)

#### PythonAnywhere

1. Зарегистрируйтесь на [pythonanywhere.com](https://www.pythonanywhere.com)

2. Загрузите файлы через веб-интерфейс или Git:
   ```bash
   git clone your-repo
   ```

3. Создайте веб-приложение:
   - Зайдите в раздел "Web"
   - Нажмите "Add a new web app"
   - Выберите Flask
   - Укажите путь к `web_app.py`

4. Настройте WSGI:
   - Откройте файл WSGI конфигурации
   - Замените на:
   ```python
   import sys
   path = '/home/yourusername/path/to/app'
   if path not in sys.path:
       sys.path.append(path)
   
   from web_app import app as application
   ```

5. Обновите настройки:
   - В `web_app.py` укажите правильный `API_CONFIG`
   - Убедитесь, что `debug=False`

6. Перезагрузите приложение

#### Heroku

1. Установите Heroku CLI

2. Создайте `Procfile`:
   ```
   web: gunicorn web_app:app
   ```

3. Создайте `runtime.txt`:
   ```
   python-3.11.0
   ```

4. Разверните:
   ```bash
   heroku create your-app-name
   git push heroku main
   heroku config:set API_BASE_URL=http://your-bot-server-ip:5001
   ```

#### Railway

1. Подключите репозиторий к Railway

2. Настройте переменные окружения:
   - `API_BASE_URL`: URL API сервера бота
   - `PORT`: автоматически устанавливается

3. Railway автоматически определит Flask приложение

### Вариант 2: VPS/Сервер (Ubuntu/Debian)

#### Установка через Gunicorn + Nginx

1. **Установите зависимости:**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   cd /var/www
   sudo mkdir webapp
   sudo chown $USER:$USER webapp
   cd webapp
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

3. **Загрузите файлы:**
   ```bash
   # Скопируйте все файлы в /var/www/webapp
   ```

4. **Создайте systemd сервис:**

   Создайте `/etc/systemd/system/webapp.service`:
   ```ini
   [Unit]
   Description=Web App Gunicorn
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/webapp
   Environment="PATH=/var/www/webapp/venv/bin"
   ExecStart=/var/www/webapp/venv/bin/gunicorn --workers 3 --bind unix:/var/www/webapp/webapp.sock web_app:app

   [Install]
   WantedBy=multi-user.target
   ```

5. **Запустите сервис:**
   ```bash
   sudo systemctl start webapp
   sudo systemctl enable webapp
   ```

6. **Настройте Nginx:**

   Создайте `/etc/nginx/sites-available/webapp`:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/webapp/webapp.sock;
       }

       location /static {
           alias /var/www/webapp/static;
       }
   }
   ```

   Активируйте:
   ```bash
   sudo ln -s /etc/nginx/sites-available/webapp /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

7. **Настройте SSL (Let's Encrypt):**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Вариант 3: Shared хостинг (cPanel, etc.)

1. **Загрузите файлы через FTP/SFTP:**
   - Загрузите все файлы в `public_html` или указанную папку

2. **Настройте Python приложение:**
   - В cPanel найдите "Setup Python App"
   - Создайте новое приложение
   - Укажите путь к `web_app.py`
   - Установите зависимости

3. **Настройте .htaccess** (если Apache):
   - Используйте предоставленный файл `.htaccess`

4. **Обновите настройки:**
   - Укажите правильный `API_CONFIG` в `web_app.py`

## Настройка статических файлов

Убедитесь, что статические файлы доступны:

```python
# В web_app.py уже должно быть:
app = Flask(__name__, static_folder='static', static_url_path='/static')
```

## Безопасность

### 1. Отключите debug режим:
```python
app.run(debug=False)
```

### 2. Используйте переменные окружения для секретов:
```python
import os
app.secret_key = os.getenv('SECRET_KEY', os.urandom(24))
```

### 3. Настройте CORS правильно:
```python
CORS(app, resources={r"/api/*": {"origins": "https://your-domain.com"}})
```

### 4. Используйте HTTPS:
- Настройте SSL сертификат
- Перенаправляйте HTTP на HTTPS

## Проверка после развертывания

1. Проверьте доступность сайта
2. Проверьте работу API (авторизация)
3. Проверьте статические файлы (CSS, JS, изображения)
4. Проверьте логи на ошибки

## Решение проблем

### Ошибка: "Module not found"
- Убедитесь, что все зависимости установлены
- Проверьте виртуальное окружение

### Ошибка: "Connection refused" к API
- Проверьте `API_CONFIG['base_url']`
- Убедитесь, что API сервер бота запущен
- Проверьте firewall настройки

### Статические файлы не загружаются
- Проверьте путь к папке `static`
- Проверьте права доступа к файлам
- Проверьте настройки Nginx/Apache

### Ошибка 500
- Проверьте логи приложения
- Проверьте логи сервера (Nginx/Apache)
- Убедитесь, что все зависимости установлены

## Полезные команды

```bash
# Проверка статуса (systemd)
sudo systemctl status webapp

# Просмотр логов
sudo journalctl -u webapp -f

# Перезапуск
sudo systemctl restart webapp

# Проверка Nginx
sudo nginx -t
sudo systemctl reload nginx
```

## Готово!

После развертывания ваш сайт будет доступен по указанному домену и будет синхронизироваться с БД бота через API.

