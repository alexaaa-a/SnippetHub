from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Favorites:
    def __init__(self, user_id, snippet_id):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.user_id = user_id
        self.snippet_id = snippet_id

    def create_favorite(self):
        """Создание новой записи в таблице."""
        cursor.execute('''
        INSERT INTO favorites (user_id, snippet_id)
        VALUES (%s, %s)''', (self.user_id, self.snippet_id))

        connection.commit()

    @staticmethod
    def is_favorite(user_id, snippet_id):
        """Проверка, находится ли сниппет в Избранном."""
        cursor.execute("""
        SELECT * FROM favorites WHERE user_id = %s AND snippet_id = %s""",
                       (user_id, snippet_id))

        result = cursor.fetchone()
        return result is not None

    @staticmethod
    def remove_favorite(user_id, snippet_id):
        """Удаление сниппета из Избранного."""
        cursor.execute(
            '''DELETE FROM favorites WHERE user_id = %s AND snippet_id = %s''',
            (user_id, snippet_id)
        )
        connection.commit()

    @staticmethod
    def get_favorites(user_id):
        """Выборка сниппетов, которые в Избранном у конкретного
        пользователя."""
        cursor.execute('''SELECT snippet_id FROM favorites
        WHERE user_id = %s''', (user_id,))
        return cursor.fetchall()

