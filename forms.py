from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class TextForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    file = FileField(validators=[FileRequired(), FileAllowed(["txt"], "Only txt files")])
    submit = SubmitField("Add new story")


class KnownForm(FlaskForm):
    text_block = TextAreaField("Paste known words here")
    submit = SubmitField("Add words to known")
