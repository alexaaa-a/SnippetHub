from werkzeug.security import generate_password_hash, check_password_hash
from flask import make_response
from models.sessions import Sessions
from flask import render_template, redirect, url_for, request, Blueprint, flash
from utils import generate_session_token
from models.users import Users
import datetime
from controllers.main_controller import main_bp

auth_bp = Blueprint('auth', __name__)

auth_bp.register_blueprint(main_bp)

@auth_bp.route('/auth.signin', methods=['GET', 'POST'])
def signin():
    """Вход пользователя, начало его сессии на сайте.
    Длительность сессии - один день с момента последнего входа.
    Также проверяется соответствие пароля хэшу. Обработка неправильного
    ввода пароля, а также пустых полей."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not Users.find_user(username):
            print('User not found')
            flash("Invalid username or password.", "danger")
            return redirect(url_for('auth.signin'))

        if not check_password_hash(Users.find_user(username)[3], password):
            flash("Invalid username or password.", "danger")
            return redirect(url_for('auth.signin'))

        user = Users.find_user(username)
        session_token = generate_session_token()
        session_expiry = datetime.datetime.now() + datetime.timedelta(days=1)

        session_entry = Sessions(user_id=user[0], session_token=session_token, expires_at=session_expiry)
        session_entry.create()

        response = make_response(redirect(url_for('auth.main.main_page')))
        response.set_cookie('session_token', session_token, httponly=True, samesite='Strict')
        return response

    return render_template('users/signin.html')


@auth_bp.route('/auth.signup', methods=['GET', 'POST'])
def signup():
    """Регистрация нового пользователя. Обработка пустых полей.
    Хэширование пароля. Добавление нового пользователя в базу данных.
    """
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        email = request.form.get('email', '').strip()
        registration_date = datetime.date.strftime(datetime.date.today(), '%Y-%m-%d')

        if not username or not password or not email:
            flash("All fields are required.", "danger")
            return redirect(url_for('auth.signup'))

        if Users.find_user(username) != 'not found':
            flash("Username is already taken.", "danger")
            return redirect(url_for('auth.signup'))

        if len(username) > 120 or len(email) > 120:
            flash('Invalid data. Username or email is too long.', 'danger')
            return redirect(url_for('auth.signup'))

        hashed_password = generate_password_hash(password)
        user = Users(name=username, email=email, password=hashed_password, registration_date=registration_date)
        user.create()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('auth.signin'))

    return render_template('users/signup.html')

@auth_bp.route('/auth.logout', methods=['GET', 'POST'])
def logout():
    """Выход пользователя. Удаление его сессии."""
    session_token = request.cookies.get('session_token')

    if session_token:
        Sessions.delete_session(session_token)

    response = make_response(redirect(url_for('auth.signin')))
    response.delete_cookie('session_token')
    flash("You have been logged out.", "success")
    return response

