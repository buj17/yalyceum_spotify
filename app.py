import sqlalchemy
from flask import Flask, render_template, request, redirect, url_for, session, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo

from db.managers.user_manager import UserManager
from db.models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'
manager = UserManager()
login_manager = LoginManager(app)

import os
from werkzeug.utils import secure_filename
from flask import send_from_directory

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


@app.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    if 'avatar' not in request.files:
        return {'success': False, 'message': 'Файл не выбран'}, 400

    file = request.files['avatar']
    if file.filename == '':
        return {'success': False, 'message': 'Файл не выбран'}, 400

    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        filename = f"user_{current_user.id}_{secure_filename(file.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Обновляем путь к аватару в базе данных
        avatar_url = f"/static/uploads/avatars/{filename}"
        manager.update_user_avatar(current_user.id, avatar_url)

        return {'success': True, 'avatar_url': avatar_url}

    return {'success': False, 'message': 'Недопустимый формат файла'}, 400


@app.route('/static/uploads/avatars/<filename>')
def uploaded_avatar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    return manager.get_user_by_id(user_id)


class RegisterForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    confirm = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class Soundtrack:
    def __init__(self, id, title, audio_url, cover_url, is_favorite=False):
        self.id = id
        self.title = title
        self.audio_url = audio_url
        self.cover_url = cover_url
        self.is_favorite = is_favorite


@login_manager.unauthorized_handler
def redirect_to_login():
    return redirect('/login')


@app.route('/')
@login_required
def home():
    soundtracks = [
        Soundtrack(1, "Трек 1", "/static/audio/track1.mp3", "/static/img/cover1.jpg", True),
        Soundtrack(2, "Трек 2", "/static/audio/track2.mp3", "/static/img/cover2.jpg", False)
    ]
    return render_template('home.html', user=current_user, soundtracks=soundtracks, title='Главная')


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('q', '').strip()
    results = []
    soundtracks = [
        Soundtrack(1, "Трек 1", "/static/audio/track1.mp3", "/static/img/cover1.jpg", True),
        Soundtrack(2, "Трек 2", "/static/audio/track2.mp3", "/static/img/cover2.jpg", False)
    ]

    return render_template('search.html', user=current_user, query=query, soundtracks=soundtracks, title='Поиск')


@app.route('/account')
@login_required
def account():
    soundtracks = [
        Soundtrack(1, "Трек 1", "/static/audio/track1.mp3", "/static/img/cover1.jpg", True)
    ]
    return render_template('account.html', soundtracks=soundtracks, user=current_user, title='Аккаунт')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        try:
            manager.add_user(user)
            login_user(manager.get_user_by_email(user.email))
            return redirect('/')
        except sqlalchemy.exc.IntegrityError as error:
            print(error)
            return render_template('register.html', massage='Уже существует пользователь с такой почтой или именем',
                                   form=form,
                                   user=user, title='Регистрация')
    return render_template('register.html', user=current_user, title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = manager.get_user_by_email(form.email.data)
            if not user.check_password(form.password.data):
                raise ValueError
            login_user(user)
            return redirect('/')
        except ValueError as e:
            return render_template('login.html', massage='Неверная почта или пароль', user=current_user, title='Войти',
                                   form=form)
    return render_template('login.html', user=current_user, title='Войти', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)
