from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Profiles:
    def __init__(self, bio, avatar_url):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.bio = bio
        self.avatar_url = avatar_url

    def create_profile(self):
        """Создание новой записи в таблице."""
        cursor.execute('''
        INSERT INTO profiles (bio, avatar_url)
        VALUES (%s, %s) RETURNING id''', (self.bio, self.avatar_url))

        profile_id = cursor.fetchone()[0]
        connection.commit()

        return profile_id

    @staticmethod
    def update_profile(avatar_url, profile_id):
        """Добавление в профиль пользователя аватарки."""
        cursor.execute('UPDATE profiles SET avatar_url = %s WHERE id = %s',
                       (avatar_url, profile_id))

        connection.commit()

    @staticmethod
    def update_bio(bio, profile_id):
        """Добавление в профиль пользователя описания профиля."""
        cursor.execute('UPDATE profiles SET bio = %s WHERE id = %s', (bio, profile_id))

        connection.commit()

