from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class SnippetTags:
    def __init__(self, snippet_id, tag_id):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.snippet_id = snippet_id
        self.tag_id = tag_id

    def create_tag(self):
        """Добавление новой записи в таблицу."""
        cursor.execute('''
        INSERT INTO snippet_tags (snippet_id, tag_id)
        VALUES (%s, %s)''', (self.snippet_id, self.tag_id))

        connection.commit()