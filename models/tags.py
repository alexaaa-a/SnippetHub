from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Tags:
    def __init__(self, name):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.name = name

    def create(self):
        """Создание новой записи в таблице"""
        cursor.execute('''
        INSERT INTO tags (name)
        VALUES (%s)''', (self.name,))

        connection.commit()

    @staticmethod
    def get_tag_by_name(name):
        """Получение id тега по его имени."""
        cursor.execute("SELECT id FROM tags WHERE name = %s", (name,))
        return cursor.fetchone()
