from flask import Flask, render_template, request, redirect, url_for, session, redirect
from flask_login import LoginManager, login_user, current_user, logout_user, UserMixin

app = Flask(__name__)
app.config['SECRET_KEY'] = '<KEY>'


class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password


user = User('qwe', '123')


@app.route('/')
def home():
    """if not current_user.is_authenticated:
        redirect(url_for('register'))"""
    return render_template('home.html', user=user, title='Главная')


@app.route('/search', methods=['GET'])
def search():
    """if not current_user.is_authenticated:
        redirect(url_for('register'))"""
    query = request.args.get('q', '').strip()
    results = []

    if query:
        mock_data = [
            {'name': 'Imagine', 'artist': 'John Lennon', 'image': '/static/images/imagine.jpg'},
            {'name': 'Bohemian Rhapsody', 'artist': 'Queen', 'image': '/static/images/bohemian.jpg'},
            {'name': 'Shape of You', 'artist': 'Ed Sheeran', 'image': '/static/images/shape.jpg'},
        ]

        results = [
            item for item in mock_data
            if query.lower() in item['name'].lower() or query.lower() in item['artist'].lower()
        ]

    return render_template('search.html', user=user, query=query, results=results, title='Поиск')


@app.route('/account')
def account():
    """if not current_user.is_authenticated:
        redirect(url_for('register'))"""
    return render_template('account.html', user=user, title='Аккаунт')


@app.route('/register', methods=['GET', 'POST'])
def register():
    pass

@app.route('/login', methods=['GET', 'POST'])
def login():
    pass

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('register'))

@app.route('/playlist/<int:playlist_id>')
def playlist(playlist_id):
    pass


if __name__ == '__main__':
    app.run('127.0.0.1', port=8080)
