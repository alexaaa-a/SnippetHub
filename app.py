from datetime import datetime

from flask import Flask, redirect, url_for
from config import Config
from controllers.auth_controller import auth_bp
from flask import g, request
from models.sessions import Sessions
from models.users import Users

app = Flask(__name__)

app.config.from_object(Config)
app.register_blueprint(auth_bp)


@app.before_request
def load_user():
    """Проверка, авторизирован ли пользователь перед каждым HTTP-запросом.
    Если пользователь залогинен, то данные о нем доступны в других частях
    приложения, если нет - пользователь приравнивается к None."""
    session_token = request.cookies.get('session_token')

    if session_token:
        session_entry = Sessions.find_session(session_token)
        if session_entry and session_entry[4] > datetime.now():
            g.user = Users.get_user_info(session_entry[1])
            print(g.user)
        else:
            g.user = None
    else:
        g.user = None


@app.route('/')
def index():
    """Первая страница сайта."""
    return redirect(url_for('auth.main.main_page'))


if __name__ == '__main__':
    app.run()
