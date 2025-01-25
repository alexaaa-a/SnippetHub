from flask import render_template, Blueprint, redirect, url_for, request, flash
from models.snippets import Snippets
from models.comments import Comments
from models.favorites import Favorites
import datetime
from models.sessions import Sessions
from controllers.profile_controller import profile_bp

main_bp = Blueprint('main', __name__)
main_bp.register_blueprint(profile_bp)

@main_bp.route('/auth.main.main_page', methods=['GET', 'POST'])
def main_page():
    """Главная страница сайта. Именно она открывается при переходе на сайт.
    На ней: лента сниппетов, возможность добавить их в Избранное, прокомментировать,
    но только при условии, что пользователь вошел на сайт. Без входа доступны
    следующие функции: просмотр сниппетов, поиск сниппетов, сортировка сниппетов
    по алфавиту."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    snippets = []
    results = Snippets.get_snippets()

    for row in results:
        snippets.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'language': row[3],
            'code': row[4],
            'author': row[5],
            'created_at': row[6],
            'tags': row[7],
            'is_favorite': Favorites.is_favorite(user_id, row[0]) if user_id else False
        })

    return render_template('main_page.html', snippets=snippets)

@main_bp.route('/auth.main.snippet/<int:snippet_id>', methods=['GET', 'POST'])
def comment_snippet(snippet_id):
    """Страница для комментирования сниппетов."""
    snippet_data = Snippets.get_snippet(snippet_id)
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if not snippet_data:
        return "Snippet not found", 404

    snippet = {
        'id': snippet_data[0],
        'title': snippet_data[1],
        'description': snippet_data[2],
        'language': snippet_data[3],
        'code': snippet_data[4],
        'author': snippet_data[5],
        'created_at': snippet_data[6],
        'tags': snippet_data[7],
        'is_favorite': Favorites.is_favorite(user_id, snippet_data[0]) if user_id else False
    }

    if request.method == 'POST':
        comment_text = request.form.get('comment')
        if user_id and comment_text:
            comment = Comments(text=comment_text, comment_date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), author_id=user_id, snippet_id=snippet_id)
            comment.create_comment()

    comments = Comments.get_comments(snippet_id)

    return render_template('snippets/snippet_details.html', snippet=snippet, comments=comments)

@main_bp.route('/auth.main.snippet_comments/<int:snippet_id>', methods=['GET', 'POST'])
def snippet_comments(snippet_id):
    """Страница просмотра комментариев к сниппету."""
    snippet_data = Snippets.get_snippet(snippet_id)
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)
    if not snippet_data:
        return "Snippet not found", 404

    snippet = {
        'id': snippet_data[0],
        'title': snippet_data[1],
        'description': snippet_data[2],
        'language': snippet_data[3],
        'code': snippet_data[4],
        'author': snippet_data[5],
        'created_at': snippet_data[6],
        'tags': snippet_data[7],
        'is_favorite': Favorites.is_favorite(user_id, snippet_data[0]) if user_id else False
    }

    comments_data = Comments.get_comments(snippet_id)
    comments = []

    for comment in comments_data:
        comments.append({
            'content': comment[0],
            'author': comment[1],
            'created_at': comment[2],
        })

    return render_template('comments/comments.html', snippet=snippet, comments=comments)

@main_bp.route('/auth.main.add_to_favorites/<int:snippet_id>', methods=['GET', 'POST'])
def add_to_favorites(snippet_id):
    """Добавление сниппета в Избранное. В случае, если сниппет уже
    добавлен к пользователю в Избранное, с помощью той же кнопки
    можно убрать сниппет из избранного, надпись на кнопке также меняется."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    if Favorites.is_favorite(user_id, snippet_id):
        Favorites.remove_favorite(user_id, snippet_id)
    else:
        fav = Favorites(user_id, snippet_id)
        fav.create_favorite()

    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('auth.main.main_page'))

@main_bp.route('/auth.main.favorites')
def favorites():
    """Страница просмотра избранных сниппетов.
    Есть возможность убрать определенный сниппет из избранного,
    а также посмотреть его подробнее."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    favs = Favorites.get_favorites(user_id)
    snippets = []
    for snippet in favs:
        data = Snippets.get_snippet(snippet)
        print(data)
        snippets.append({
            'id': data[0],
            'title': data[1],
            'description': data[2],
            'language': data[3],
            'code': data[4],
            'author': data[5],
            'created_at': data[6],
            'tags': data[7],
            'is_favorite': Favorites.is_favorite(user_id, data[0]) if user_id else False
        })

    return render_template('favorites/favorites.html', snippets=snippets)

@main_bp.route('/auth.main.remove_from_favorites/<int:snippet_id>', methods=['GET', 'POST'])
def remove_from_favorites(snippet_id):
    """Возможность убрать сниппет из Избранного."""
    session_token = request.cookies.get('session_token')
    user_id = Sessions.get_user_id_by_token(session_token)

    if user_id is None:
        return redirect(url_for('auth.signin'))

    Favorites.remove_favorite(user_id, snippet_id)

    return redirect(url_for('auth.main.favorites'))

@main_bp.route('/auth.main.search', methods=['GET', 'POST'])
def search_snippets():
    """Поиск сниппета по названию или описанию."""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query or len(query) > 50:
            flash("Search query cannot be empty or exceed 50 characters.", "danger")
            return redirect(url_for('auth.main.main_page'))

        snippets = Snippets.search_snippets(query)
        return render_template('snippets/search_results.html', snippets=snippets, query=query)

    return redirect(url_for('profile.profile'))


