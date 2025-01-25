from app import Config
import psycopg2
from models.profiles import Profiles

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Users:
    def __init__(self, name, email, password, registration_date):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.name = name
        self.email = email
        self.password = password
        self.registration_date = registration_date

    def create(self):
        """Добавление новой записи в таблицу."""
        profile = Profiles(bio='', avatar_url='')
        profile_id = profile.create_profile()

        cursor.execute('''
        INSERT INTO users (name, email, password, registration_date, profile_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;''',
                       (self.name, self.email, self.password, self.registration_date, profile_id))

        user_id = cursor.fetchone()[0]
        connection.commit()
        return user_id

    @staticmethod
    def find_user(username: str):
        """Нахождение пользователя по его имени."""
        cursor.execute('SELECT * FROM users WHERE name = %s', (username,))
        user_data = cursor.fetchone()
        if user_data:
            return user_data
        return 'not found'

    @staticmethod
    def get_user_info(user_id):
        """Получение сведений о пользователе по его id."""
        cursor.execute('''
            SELECT users.id, users.name, users.email, profiles.avatar_url, profiles.bio 
            FROM users
            JOIN profiles ON users.profile_id = profiles.id
            WHERE users.id = %s;
            ''', (user_id,))
        user_data = cursor.fetchone()

        return user_data

    @staticmethod
    def get_profile_info(user_id):
        """Получение id профиля пользователя по его id."""
        cursor.execute('SELECT profile_id FROM users WHERE id = %s', (user_id,))
        return cursor.fetchone()




