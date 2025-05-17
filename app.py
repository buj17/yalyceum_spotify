import secrets
from typing import Sequence

from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_login import LoginManager, login_user, current_user, logout_user, login_required

from db.connect import create_session
from db.managers.music_manager import MusicManager
from db.managers.user_manager import UserManager, EmailAlreadyExistsError
from db.models import User, Music
from forms import LoginForm, RegistrationForm

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(64)

login_manager = LoginManager(app)

# Добавим конфигурацию для загрузки файлов
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2MB max


@app.route("/update_avatar", methods=["POST"])
@login_required
def update_avatar():
    if "avatar" not in request.files:
        return jsonify({"success": False, "message": "Файл не найден"}), 400

    file = request.files["avatar"]

    if file:
        try:
            user_manager = UserManager()
            content = file.read()

            user_manager.upload_avatar(current_user.id, content)

            avatar_url = user_manager.get_avatar_url(current_user.id)

            return jsonify({"success": True, "avatar_url": avatar_url})

        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400

    return jsonify({"success": False, "message": "Ошибка при обработке файла"}), 400


@login_manager.user_loader
def load_user(user_id: int) -> User | None:
    user_manager = UserManager()
    return user_manager.get_user_by_id(user_id)


@login_manager.unauthorized_handler
def redirect_to_login():
    return redirect("/login")


def urls_dictionary_getter(tracks: Sequence[type[Music] | Music]):
    soundtracks = [track.id for track in tracks]
    with create_session() as db_session:
        music_manager = MusicManager(db_session)
        urls = music_manager.get_music_url_pairs(*soundtracks)
        res = [
            {
                "track": track,
                "track_url": track_url,
                "img_url": img_url
            }
            for track, (track_url, img_url) in zip(tracks, urls)
        ]
        return res


@app.route("/")
@login_required
def home():
    with create_session() as db_session:
        music_manager = MusicManager(db_session)
        user_manager = UserManager()
        temporal_soundtracks = music_manager.get_random_music()
        res = urls_dictionary_getter(temporal_soundtracks)
        return render_template("home.html",
                               user=current_user,
                               soundtracks=temporal_soundtracks,
                               title="Главная",
                               user_manager=user_manager,
                               res=res)


@app.route("/search", methods=["GET"])
@login_required
def search():
    with create_session() as db_session:
        music_manager = MusicManager(db_session)
        user_manager = UserManager()
        query = request.args.get("q", "").strip()
        if query:
            result = music_manager.search_music(query)
        else:
            result = []
        res = urls_dictionary_getter(result)
        return render_template("search.html",
                               user=current_user,
                               query=query,
                               title="Поиск",
                               user_manager=user_manager,
                               res=res)


@app.route("/account")
@login_required
def account():
    user_manager = UserManager()
    favorite_music = user_manager.get_favorite_tracks(current_user.id)
    res = urls_dictionary_getter(favorite_music)
    return render_template("account.html",
                           user=current_user,
                           title="Аккаунт",
                           user_manager=user_manager,
                           res=res)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    user_manager = UserManager()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        try:
            user_manager.add_user(user)
            login_user(user)
            return redirect("/")
        except EmailAlreadyExistsError:
            return render_template("register.html",
                                   message="Уже существует пользователь с такой почтой",
                                   form=form,
                                   user=user,
                                   title="Регистрация")

    return render_template("register.html",
                           user=current_user,
                           title="Регистрация",
                           form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user_manager = UserManager()
            user = user_manager.get_user_by_email(form.email.data)
            if not user.check_password(form.password.data):
                raise ValueError
            login_user(user)
            return redirect("/")
        except ValueError:
            return render_template("login.html",
                                   massage="Неверная почта или пароль",
                                   user=current_user,
                                   title="Войти",
                                   form=form)

    return render_template("login.html",
                           user=current_user,
                           title="Войти",
                           form=form)


@app.route("/toggle_favorite/<int:track_id>", methods=["POST"])
@login_required
def toggle_favorite(track_id: int):
    user_manager = UserManager()
    if not user_manager.is_favorite(current_user.id, track_id):
        user_manager.add_favorite_track(current_user.id, track_id)
    else:
        user_manager.remove_favorite_track(current_user.id, track_id)
    return "", 204


@app.route("/logout", methods=["GET", "POST"])
def logout():
    logout_user()
    return redirect(url_for("login"))
