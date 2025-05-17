from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import EqualTo, DataRequired, Email


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        DataRequired(message="Введите имя пользователя")
    ])
    email = EmailField("Email", validators=[
        DataRequired(message="Введите email"),
        Email(message="Неправильный формат email")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Введите пароль")
    ])
    confirm = PasswordField("Repeat Password", validators=[
        DataRequired(message="Введите пароль повторно"),
        EqualTo("password", message="Введенные пароли не совпадают")
    ])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[
        DataRequired(message="Введите email"),
        Email(message="Неправильный формат email")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Введите пароль")
    ])
    submit = SubmitField("Login")
