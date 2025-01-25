from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Snippets:
    def __init__(self, title, description, language, code, author_id, created_at):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.title = title
        self.description = description
        self.language = language
        self.code = code
        self.author_id = author_id
        self.created_at = created_at

    def create_snippet(self):
        """Добавление новой записи в таблицу."""
        cursor.execute('''
        INSERT INTO snippets (title, description, language, code, author_id)
        VALUES (%s, %s, %s, %s, %s)''', (self.title, self.description, self.language, self.code, self.author_id))

        connection.commit()

    @staticmethod
    def get_snippets():
        """Получение всех сниппетов с дополнительными данными из
        других таблиц."""
        cursor.execute('''
            SELECT 
                snippets.id,
                snippets.title,
                snippets.description,
                snippets.language,
                snippets.code,
                users.name AS author,
                snippets.created_at,
                ARRAY_AGG(tags.name) AS tags
            FROM snippets
            JOIN users ON snippets.author_id = users.id
            LEFT JOIN snippet_tags ON snippets.id = snippet_tags.snippet_id
            LEFT JOIN tags ON snippet_tags.tag_id = tags.id
            GROUP BY snippets.id, users.name, snippets.created_at
            ORDER BY snippets.created_at DESC;
            ''')
        results = cursor.fetchall()

        return results

    @staticmethod
    def get_snippet_by_id(user_id):
        """Получение сниппетов, созданных определенным пользователем."""
        cursor.execute('''
            SELECT id, title, description, language, created_at, author_id
            FROM snippets 
            WHERE author_id = %s
            ORDER BY created_at DESC;
            ''', (user_id,))
        user_snippets = cursor.fetchall()

        return user_snippets

    @staticmethod
    def get_snippet(snippet_id):
        """Получение одного сниппета по его id."""
        cursor.execute('''
                    SELECT 
                        snippets.id,
                        snippets.title,
                        snippets.description,
                        snippets.language,
                        snippets.code,
                        users.name AS author,
                        snippets.created_at,
                        ARRAY_AGG(tags.name) AS tags
                    FROM snippets
                    JOIN users ON snippets.author_id = users.id
                    LEFT JOIN snippet_tags ON snippets.id = snippet_tags.snippet_id
                    LEFT JOIN tags ON snippet_tags.tag_id = tags.id
                    WHERE snippets.id = %s
                    GROUP BY snippets.id, users.name;
                    ''', (snippet_id,))

        snippet = cursor.fetchall()
        return snippet[0]

    def get_id(self):
        """Получение id сниппета."""
        cursor.execute('''
        SELECT id FROM snippets
        WHERE title = %s AND description = %s AND language = %s AND code = %s
        AND author_id = %s''',
                       (self.title, self.description, self.language, self.code, self.author_id))

        return cursor.fetchone()

    @staticmethod
    def delete(snippet_id):
        """Удаление сниппета."""
        cursor.execute('''
        DELETE FROM snippets WHERE id = %s''', (snippet_id,))

        connection.commit()

    @staticmethod
    def update_snippet(snippet_id, title, description, language, code, created_at):
        """Редактирование сниппета."""
        cursor.execute('''
                UPDATE snippets
                SET title = %s, description = %s, language = %s, code = %s, created_at = %s
                WHERE id = %s
            ''', (title, description, language, code, created_at, snippet_id,))
        connection.commit()

    @staticmethod
    def get_author_id(snippet_id):
        """Получение id автора определенного сниппета."""
        cursor.execute('''
        SELECT author_id FROM snippets WHERE id = %s''', (snippet_id,))

        return cursor.fetchone()

    @staticmethod
    def search_snippets(query):
        """Поиск сниппета по названию и описанию."""
        cursor.execute('''
                SELECT id, title, description, language, created_at, author_id
                FROM snippets
                WHERE title ILIKE %s OR description ILIKE %s
            ''', (f'%{query}%', f'%{query}%'))

        results = cursor.fetchall()
        snippets = [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'language': row[3],
                'created_at': row[4],
                'author_id': row[5]
            }
            for row in results
        ]

        return snippets