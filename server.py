from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re

app = Flask(__name__)
app.secret_key = "supersecret"


mysql = MySQLConnector(app, 'walldb')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route('/')
def index():
    """Display index with login and registration forms."""
    return render_template('index.html')


@app.route('/login')
def login():
    """Allow users to log in.

    Validate credentials against user in database and save user id to session.
    Then redirect to the wall.
    """


@app.route('/register')
def register():
    """Register new users.

    Validate registration form input. Add valid form entries to the database.
    Then log the registered user in and redirect to wall.
    """


@app.route('/wall')
def wall():
    """Display the wall page.

    The wall shows posts in descending chronological order. Users may post new
    messages and comment on existing messages. Message comments are also displayed in
    descending chron order.
    """
    return render_template('wall.html')


@app.route('/post')
def post():
    """Post a message on the wall."""


@app.route('/comment')
def comment():
    """Comment on an existing message."""


app.run(debug=True)
