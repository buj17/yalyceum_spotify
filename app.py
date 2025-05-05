from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, current_user
from forms import RegistrationForm, LoginForm
from db import funcs

app = Flask(__name__)
app.config[
    "SECRET_KEY"] = "your-secret-key-here-change-me"  # Измените на надежный ключ!

# Инициализация Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """Загрузка пользователя для Flask-Login"""
    return funcs.get_user_by_id(int(user_id))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    print(4)
    if form.validate_on_submit():
        try:
            if funcs.get_user_by_username(form.username.data):
                return redirect(url_for('register'))
            print(1)
            if funcs.get_user_by_email(form.email.data):
                return redirect(url_for('register'))
            print(2)
            funcs.create_user(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data
            )
            print(3)
            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')
    print("пидарас", form.errors)
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    print(1)
    if form.validate_on_submit():
        print(2)
        user = funcs.get_user_by_username(form.username.data)
        print(3)
        if user and user.check_password(form.password.data):    # здесь ошиьбка
            print(4)
            login_user(user)
            return redirect(url_for('index'))
    print(form.errors, 5)
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    funcs.download_music_cover_and_push_into_s3_and_db("love")
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)