import os
from functools import wraps

import flask
from flask import Flask, render_template, redirect, url_for
from flask_bs4 import Bootstrap
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from forms import LoginForm, RegisterForm, TextForm, KnownForm
from my_parser import Parser

APP_NAME = "Riduridu"

app = Flask(__name__)
Bootstrap(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
uri = os.getenv("DATABASE_URL", "sqlite:///base.db")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
    print(uri)


@app.context_processor
def context_processor():
    context_dict = {
        "APP_NAME": APP_NAME,
        "user_auth": current_user.is_authenticated
    }
    return context_dict


# Databases
Base = declarative_base()
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    stories = relationship("Story", back_populates="user")


class Story(db.Model):
    __tablename__ = "story"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    filepath = db.Column(db.String, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User", back_populates="stories")

def login_required(function):
    @wraps(function)
    def wrapper_function(*args, **kwargs):
        if current_user.is_authenticated:
            return function(*args, **kwargs)
        else:
            return redirect(url_for("about"))

    return wrapper_function


db.create_all()

# Auth
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


parser = Parser()


@app.route("/")
def main_page():
    return redirect(url_for("about"))


@app.route('/home')
@login_required
def home():
    # TODO make it more beautiful
    filenames = os.listdir(f'static/users/{current_user.id}/stories')
    return render_template("home.html", title=APP_NAME, stories=filenames)


@app.route('/<story_name>/<int:page_number>')
@login_required
def show_story(story_name, page_number):
    if page_number == 0:
        return "Error"
    page_number -= 1
    with open(f"static/users/{current_user.id}/stories/{story_name}", "r", encoding="utf-8") as file:
        text = file.read()
    k = text.replace("\n\n", "\n").replace("\u3000", "")
    paragraphs = k.split("\n")
    pages = []
    page = []
    page_count = 0
    for paragraph in paragraphs:
        page_count += len(paragraph)
        if page_count < 1000:
            page.append(paragraph)
        elif page == len(paragraph):
            pages.append(page)
            page_count = 0
        else:
            pages.append(parser.parse_list(page))
            page_count = len(paragraph)
            page = [paragraph]
    if page:
        pages.append(parser.parse_list(page))

    return render_template("story.html", title=APP_NAME, story_name=story_name, page_number=page_number,
                           paragraphs=pages[page_number], page_count=len(pages), dict=parser.dict)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter_by(username=username).first()
        if user:
            password = form.password.data
            if check_password_hash(user.password, password):
                flask.flash("Logged in successfully")
                login_user(user)
                global parser
                parser.dict = parser.parse_known(current_user.id)
                return redirect(url_for("home"))
            else:
                form.password.errors.append("Password is wrong")
        else:
            form.username.errors.append("Username doesn't exist")

    return render_template("forms.html", form=form, form_use="Login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("about"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = KnownForm()
    if form.validate_on_submit():
        old_dict = parser.parse_known(current_user.id)
        text = form.text_block.data
        morphs = parser.parse_text(text)
        dict = parser.format_data(morphs)
        dict.update(old_dict)
        with open(f"static/users/{current_user.id}/data/known.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(dict.keys()))
        parser.add_known(user_id=current_user.id)
        return redirect(url_for("home"))
    return render_template("forms.html", form=form, form_use="Profile")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        if User.query.filter_by(username=username).first():
            form.username.errors.append("Username already exists")
        else:
            password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            path = f"static/users/"
            try:
                os.mkdir(path)
            except FileExistsError:
                pass
            path += f"{new_user.id}/"
            os.mkdir(path)
            os.mkdir(path + "stories")
            os.mkdir(path + "data")
            with open(path + "data/known.txt", "w", encoding="utf-8"):
                pass
            parser.dict = {}
            flask.flash("Your registration was successful")
            login_user(new_user)

            return redirect(url_for("home"))
    return render_template("forms.html", form=form, form_use="Register")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_story():
    form = TextForm()
    if form.validate_on_submit():
        title = form.title.data
        if Story.query.filter_by(title=title).first():
            form.title.errors.append("Story with that title already exists")
        else:
            file = form.file.data
            path = f"static/users/{current_user.id}/stories/{title}.txt"
            file.save(dst=path)
            new_story = Story(title=title, filepath=path)
            db.session.add(new_story)
            db.session.commit()
            flask.flash("Story added successfully")

    return render_template("forms.html", form=form, form_use="Add new story")


if __name__ == '__main__':
    app.run(debug=True)
