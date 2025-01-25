from app import Config
import psycopg2

db = Config.DATABASE_CONFIG
connection = psycopg2.connect(user=db['user'], password=db['password'], host=db['host'],
                              port=db['port'], database=db['dbname'])
cursor = connection.cursor()

class Sessions:
    def __init__(self, user_id, session_token, expires_at):
        """Инициализация всех данных, необходимых для создания новой записи
        в таблице."""
        self.user_id = user_id
        self.session_token = session_token
        self.expires_at = expires_at

    @staticmethod
    def find_session(token):
        """Поиск сессии по токену."""
        cursor.execute("SELECT * FROM sessions WHERE session_token = %s", (token,))
        return cursor.fetchone()

    @staticmethod
    def delete_session(token):
        """Удаление сессии."""
        cursor.execute("DELETE FROM sessions WHERE session_token = %s", (token,))

    def create(self):
        """Создание новой записи в таблице."""
        cursor.execute(
            "INSERT INTO sessions (user_id, session_token, expires_at) VALUES (%s, %s, %s)",
            (self.user_id, self.session_token, self.expires_at)
        )

    @staticmethod
    def get_user_id_by_token(session_token):
        """Нахождение id пользователя по токену сессии."""
        cursor.execute("SELECT user_id FROM sessions WHERE session_token = %s", (session_token,))
        session_entry = cursor.fetchone()
        if session_entry:
            return session_entry[0]
        return None