from flask import render_template, request, redirect, url_for, session, Blueprint, flash
from werkzeug.utils import secure_filename
import os
from models.profiles import Profiles
from models.sessions import Sessions
from models.users import Users
from models.snippets import Snippets
from models.favorites import Favorites
from models.tags import Tags
from models.snippet_tags import SnippetTags
import datetime

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    """Проверка соответствия файла аватарки профиля критериям."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@profile_bp.route('/auth.main.profile.profile', methods=['GET', 'POST'])
def profile():
    """Профиль пользователя. Есть возможность установить аватарку и описание
    профиля, создать сниппет, редактировать и удалять свои сниппеты. В профиле
    отображаются только сниппеты, созданные этим пользователем. Также при
    удалении сниппета требуется подтверждение."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    user_data = Users.get_user_info(user_id)
    profile_id = Users.get_profile_info(user_id)

    user = {
        'name': user_data[1],
        'email': user_data[2],
        'avatar': user_data[3],
        'description': user_data[4],
    }

    if request.method == 'POST':
        if 'avatar' in request.files:
            avatar = request.files['avatar']
            if avatar and allowed_file(avatar.filename):
                filename = secure_filename(avatar.filename)
                avatar_path = os.path.join(UPLOAD_FOLDER, filename)
                avatar.save(avatar_path)
                avatar_url = f'/static/uploads/avatars/{filename}'

                Profiles.update_profile(avatar_url, profile_id)

        description = request.form.get('description')
        if description:
            Profiles.update_bio(description, profile_id)

        return redirect(url_for('auth.main.profile.profile'))

    user_snippets = Snippets.get_snippet_by_id(user_id)

    snippets = [
        {
            'id': snippet[0],
            'title': snippet[1],
            'description': snippet[2],
            'language': snippet[3],
            'created_at': snippet[4],
            'author_id': snippet[5],
            'is_favorite': Favorites.is_favorite(user_id, snippet[0]) if user_id else False
        }
        for snippet in user_snippets
    ]

    return render_template('profiles/profile.html', user=user, snippets=snippets)


@profile_bp.route('/auth.main.profile.snippet/create', methods=['GET', 'POST'])
def create_snippet():
    """Создание нового сниппета. Все поля обязательны к заполнению.
    Новый сниппет добавляется в базу данных."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        language = request.form.get('language')
        code = request.form.get('code')
        author_id = user_id
        tags_input = request.form.get('tags')
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        errors = []
        if not title or len(title) > 100:
            errors.append("Title is required and must not exceed 100 characters.")
        if not description:
            errors.append("Description is required.")
        if not language:
            errors.append("Language is required.")
        if not code:
            errors.append("Code is required.")
        if not tags_input:
            errors.append("Tags is required.")

        if errors:
            for error in errors:
                flash(error, "danger")

        snippet = Snippets(title=title, description=description, language=language, code=code, author_id=author_id, created_at=created_at)
        snippet.create_snippet()

        tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]

        for tag_name in tags:
            tag = Tags.get_tag_by_name(tag_name)
            if not tag:
                tag = Tags(name=tag_name)
                tag.create()
            print(snippet.get_id())

            snippet_tag = SnippetTags(snippet_id=snippet.get_id(), tag_id=Tags.get_tag_by_name(tag_name))
            snippet_tag.create_tag()

        flash("Snippet created successfully.", "success")
        return redirect(url_for('auth.main.profile.profile'))

    return render_template('snippets/create_snippet.html')

@profile_bp.route('/auth.main.profile.delete_snippet/<int:snippet_id>', methods=['POST'])
def delete_snippet(snippet_id):
    """Удаление сниппета. Доступно только создателю сниппета.
    При удалении требуется подтверждение."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    author_id = Snippets.get_author_id(snippet_id)[0]

    if author_id and user_id == author_id:
        Snippets.delete(snippet_id)
    else:
        return "You are not authorized to edit this snippet.", 403

    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('auth.main.main_page'))

@profile_bp.route('/snippet/edit/<int:snippet_id>', methods=['GET', 'POST'])
def edit_snippet(snippet_id):
    """Редактирование сниппета."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)
    snippet = Snippets.get_snippet(snippet_id)
    profile_id = Snippets.get_author_id(snippet_id)[0]

    if user_id is None:
        return redirect(url_for('auth.signin'))

    new_sn = {
        'id': snippet[0],
        'title': snippet[1],
        'description': snippet[2],
        'language': snippet[3],
        'code': snippet[4],
    }

    if not profile_id or profile_id != user_id:
        return "You are not authorized to edit this snippet.", 403

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        language = request.form.get('language')
        code = request.form.get('code')
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        Snippets.update_snippet(snippet_id, title, description, language, code, created_at)
        return redirect(url_for('auth.main.profile.profile'))

    return render_template('snippets/edit_snippet.html', snippet=new_sn)

