import os
import secrets

from flask import Flask, render_template, request, url_for, redirect, jsonify, flash
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


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
AVATAR_UPLOAD_FOLDER = 'static/uploads/avatars'
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB




@app.route('/upload_avatar', methods=['POST'])
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('account'))

    file = request.files['avatar']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('account'))

    if not (file and allowed_file(file.filename)):
        flash('Недопустимый формат файла', 'danger')
        return redirect(url_for('account'))

    # Проверка размера файла
    file.seek(0, os.SEEK_END)
    if file.tell() > MAX_AVATAR_SIZE :
        flash('Файл слишком большой (максимум 2MB)', 'danger')
        return redirect(url_for('account'))
    file.seek(0)

    try:
        # Используем ваш метод для загрузки
        user_manager.upload_avatar(current_user.id, file.read())
        flash('Аватар успешно обновлен', 'success')
    except ValueError as e:
        flash(f'Ошибка: {str(e)}', 'danger')
    except Exception as e:
        flash('Произошла ошибка при загрузке', 'danger')
        app.logger.error(f"Avatar upload error: {str(e)}")

    return redirect(url_for('account'))




@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return user_manager.get_user_by_id(user_id)


@login_manager.unauthorized_handler
def redirect_to_login():
    return redirect('/login')


@app.route('/')
@login_required
def home():
    temporal_soundtracks = music_manager.search_music('pilla')
    return render_template('home.html', user=current_user, soundtracks=temporal_soundtracks, title='Главная',
                           user_manager=user_manager, music_manager=music_manager)


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip()
    if query:
        result = music_manager.search_music(query)
    else:
        result = []

    return render_template('search.html', user=current_user, query=query, soundtracks=result, title='Поиск',
                           user_manager=user_manager, music_manager=music_manager)


@app.route('/account')
@login_required
def account():
    favorite_music = user_manager.get_favorite_tracks(current_user.id)
    return render_template('account.html', soundtracks=favorite_music, user=current_user, title='Аккаунт',
                           music_manager=music_manager, user_manager=user_manager)


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
    app.run('127.0.0.1', port=8080)
