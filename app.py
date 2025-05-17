import os
import secrets

from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from flask import send_from_directory

from db.connect import create_session
from db.managers.music_manager import MusicManager
from db.managers.user_manager import UserManager, EmailAlreadyExistsError
from db.models import User
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(64)

# Менеджеры
db_session = create_session()
user_manager = UserManager()
music_manager = MusicManager(db_session)
login_manager = LoginManager(app)

# Добавим конфигурацию для загрузки файлов
UPLOAD_FOLDER = 'static/uploads/avatars'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

# Создаем папку для загрузок, если ее нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    if 'avatar' not in request.files:
        return jsonify({'success': False, 'message': 'Файл не найден'}), 400

    file = request.files['avatar']

    if file:
        try:
            content = file.read()

            user_manager.upload_avatar(current_user.id, content)

            avatar_url = user_manager.get_avatar_url(current_user.id)

            return jsonify({'success': True, 'avatar_url': avatar_url})

        except ValueError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

    return jsonify({'success': False, 'message': 'Ошибка при обработке файла'}), 400


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return user_manager.get_user_by_id(user_id)


@login_manager.unauthorized_handler
def redirect_to_login():
    return redirect('/login')


def urls_dictionary_getter(tracks):
    tracks = [track.id for track in tracks]
    urls = music_manager.get_music_url_pairs(*tracks)
    res = [{'track': track, 'track_url': track_url, 'img_url':img_url} for track, (track_url, img_url) in zip(tracks, urls)]
    return res


@app.route('/')
@login_required
def home():
    temporal_soundtracks = music_manager.search_music('pilla')
    res = urls_dictionary_getter(temporal_soundtracks)
    return render_template('home.html', user=current_user, soundtracks=temporal_soundtracks, title='Главная',
                           user_manager=user_manager, music_manager=music_manager, res=res)


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip()
    if query:
        result = music_manager.search_music(query)
        print(type(result))
    else:
        result = []

    return render_template('search.html', user=current_user, query=query, soundtracks=result, title='Поиск',
                           user_manager=user_manager, music_manager=music_manager)


@app.route('/account')
@login_required
def account():
    favorite_music = user_manager.get_favorite_tracks(current_user.id)
    res = urls_dictionary_getter(favorite_music)
    return render_template('account.html', soundtracks=favorite_music, user=current_user, title='Аккаунт',
                           music_manager=music_manager, user_manager=user_manager, res=res)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        try:
            user_manager.add_user(user)
            login_user(user)
            return redirect('/')
        except EmailAlreadyExistsError:
            return render_template('register.html', massage='Уже существует пользователь с такой почтой или именем',
                                   form=form,
                                   user=user, title='Регистрация')
    return render_template('register.html', user=current_user, title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = user_manager.get_user_by_email(form.email.data)
            if not user.check_password(form.password.data):
                raise ValueError
            login_user(user)
            return redirect('/')
        except ValueError:
            return render_template('login.html', massage='Неверная почта или пароль', user=current_user, title='Войти',
                                   form=form)
    return render_template('login.html', user=current_user, title='Войти', form=form)


@app.route('/toggle_favorite/<int:track_id>', methods=['POST'])
@login_required
def toggle_favorite(track_id: int):
    if not user_manager.is_favorite(current_user.id, track_id):
        user_manager.add_favorite_track(current_user.id, track_id)
    else:
        user_manager.remove_favorite_track(current_user.id, track_id)
    return '', 204


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


db_session.close()

if __name__ == '__main__':
    app.run('0.0.0.0')
