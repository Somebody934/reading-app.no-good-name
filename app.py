import os

from flask import Flask, render_template, redirect, url_for
from flask_bs4 import Bootstrap

APP_NAME = "Aplikacija"
app = Flask(__name__)
Bootstrap(app)


def env(value, key):
    return os.getenv(key, value)


app.add_template_filter(env)


@app.route('/')
def home():  # put application's code here
    filenames = os.listdir('static/stories/')
    return render_template("home.html", title=APP_NAME, stories=filenames)


@app.route('/<story_name>/<int:page_number>')
def show_story(story_name, page_number):
    if page_number != 0:
        page_number -= 1
    with open(f"static/stories/{story_name}", "r", encoding="utf-8") as file:
        text = file.read()
    k = text.replace("\n\n", "\n").replace("\u3000", "")
    paragraphs = k.split("\n")
    pages = []
    page = []
    page_count = 0
    i = 0
    while paragraphs:
        for paragraph in paragraphs:
            page_count += len(paragraph)
            if page_count < 1000:
                page.append(paragraph)
                i += 1
            elif page == len(paragraph):
                pages.append(page)
                page_count = 0
                paragraphs = paragraphs[i + 1::]
            else:
                pages.append(page)
                page_count = 0
                page = []
                paragraphs = paragraphs[i + 1::]
    # print(pages)
    return render_template("story.html", title=APP_NAME, page_number=page_number, paragraphs=pages[page_number], page_count=len(pages))


@app.route("/login")
def login():
    return redirect(url_for("home"))


@app.route("/register")
def register():
    return redirect(url_for("home"))


@app.route("/about")
def about():
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run()
