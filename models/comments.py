from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Comments:
    def __init__(self, text, comment_date, author_id, snippet_id):
        """Инициализация данных, необходимых для таблицы в базе данных."""
        self.text = text
        self.comment_date = comment_date
        self.author_id = author_id
        self.snippet_id = snippet_id

    def create_comment(self):
        """Создание новой записи в таблице."""
        cursor.execute('''
        INSERT INTO comments (text, comment_date, author_id, snippet_id)
        VALUES (%s, %s, %s, %s)''', (self.text, self.comment_date, self.author_id, self.snippet_id))

        connection.commit()

    @staticmethod
    def get_comments(snippet_id):
        """Функция для получения всех комментариев, которые
        относятся к конкретному сниппету."""
        cursor.execute('''
            SELECT comments.text, users.name AS author, comments.comment_date
            FROM comments
            JOIN users ON comments.author_id = users.id
            WHERE comments.snippet_id = %s
            ORDER BY comments.comment_date DESC;
            ''', (snippet_id,))

        return cursor.fetchall()

