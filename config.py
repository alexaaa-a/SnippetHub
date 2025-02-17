from dotenv import load_dotenv
import os

class Config:
    """Секретный ключ и данные для подключения базы данных."""
    SECRET_KEY = os.getenv('SECRET_KEY')

    load_dotenv()
    DATABASE_CONFIG = {
        'dbname': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT')
    }
