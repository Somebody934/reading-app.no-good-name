import os
from my_parser import Parser
from flask import Flask, render_template, redirect, url_for
from flask_bs4 import Bootstrap

APP_NAME = "Aplikacija"
app = Flask(__name__)
Bootstrap(app)

stories = {}
def env(value, key):
    return os.getenv(key, value)


app.add_template_filter(env)


@app.route('/')
def home():
    # TODO make it more beautiful
    filenames = os.listdir('static/stories/')
    return render_template("home.html", title=APP_NAME, stories=filenames)


@app.route('/<story_name>/<int:page_number>')
def show_story(story_name, page_number):
    if page_number == 0:
        return "Error"
    page_number -= 1
    if not (story_name in stories):
        with open(f"static/stories/{story_name}", "r", encoding="utf-8") as file:
            text = file.read()
        k = text.replace("\n\n", "\n").replace("\u3000", "")
        paragraphs = k.split("\n")
        pages = []
        page = []
        page_count = 0
        i = 0
        for paragraph in paragraphs:
            page_count += len(paragraph)
            if page_count < 1000:
                page.append(paragraph)
            elif page == len(paragraph):
                pages.append(page)
                page_count = 0
            else:
                pages.append(Parser().parse_list(page))
                page_count = len(paragraph)
                page = [paragraph]
        if page:
            pages.append(Parser().parse_list(page))
        stories[story_name] = pages
    else:
        pages = stories[story_name]

    return render_template("story.html", title=APP_NAME, story_name=story_name, page_number=page_number, paragraphs=pages[page_number], page_count=len(pages))


@app.route("/login")
def login():
    # TODO create login form and authentication
    return redirect(url_for("home"))


@app.route("/register")
def register():
    # TODO create register form and authentication
    return redirect(url_for("home"))


@app.route("/about")
def about():
    # TODO create about page
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run()
