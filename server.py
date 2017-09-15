import re
import md5
import os
import binascii
from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from sqlalchemy import exc

app = Flask(__name__)
app.secret_key = "supersecret"


mysql = MySQLConnector(app, 'walldb')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


@app.route('/')
def index():
    """Display index with login and registration forms."""
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    """Allow users to log in.

    Validate credentials against user in database and save user id to session.
    Then redirect to the wall.
    """
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE users.email = :email LIMIT 1"
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)
    if len(user) > 0:
        encrypted_password = md5.new(password + user[0]['salt']).hexdigest()
        if user[0]['password'] == encrypted_password:
            session['id'] = user[0]['id']
            return redirect('/wall')
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    """Clear session."""
    session.clear()
    return redirect('/')


@app.route('/register', methods=['POST'])
def register():
    """Register new users.

    Validate registration form input. Add valid form entries to the database.
    Then log the registered user in and redirect to wall.
    """
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']
    salt = binascii.b2a_hex(os.urandom(15))
    hashed_pw = md5.new(password + salt).hexdigest()
    if len(name) > 0 and len(email) > 7 and len(password) > 0 and password == confirm and EMAIL_REGEX.match(email):
        query = 'INSERT INTO users (name, email, password, created_at, updated_at, salt) VALUES (:name, :email, :password, NOW(), NOW(), :salt)'
        data = {
            'name': name,
            'email': email,
            'password': hashed_pw,
            'salt': salt,
        }
        try:
            session['id'] = mysql.query_db(query, data)
            return redirect('/wall')
        except exc.IntegrityError:
            flash('email already used')
            return redirect('/')
    elif not EMAIL_REGEX.match(email) or not len(email) > 7:
        flash('Please submit a valid email')
        return redirect('/')
    else:
        flash('All form fields must be filled out')
        return redirect('/')


@app.route('/wall')
def wall():
    """Display the wall page.

    The wall shows posts in descending chronological order. Users may post new
    messages and comment on existing messages. Message comments are also
    displayed in descending chron order.
    """
    comments = mysql.query_db('SELECT comments.comment, comments.created_at, comments.updated_at, comments.messages_id, users.name FROM comments JOIN users ON users.id = comments.users_id ORDER BY comments.created_at ASC;')
    messages = mysql.query_db('SELECT users.name, messages.id, messages.message, messages.created_at, messages.updated_at FROM messages JOIN users ON messages.users_id = users.id ORDER BY messages.created_at DESC;')
    comments_dict = {message['id']: [comment for comment in comments if comment['messages_id'] == message['id']] for message in messages}
    return render_template('wall.html', messages=messages, comments=comments_dict)


@app.route('/post', methods=['POST'])
def post():
    """Post a message on the wall."""
    message = request.form['message']
    if len(message) > 0:
        query = "INSERT INTO messages (users_id, message, created_at, updated_at) VALUES (:user_id, :message, NOW(), NOW())"
        data = {
            'user_id': session['id'],
            'message': message,
        }
        mysql.query_db(query, data)
    return redirect('/wall')


@app.route('/comment', methods=['POST'])
def make_comment():
    """Comment on an existing message."""
    comment = request.form['comment']
    messages_id = request.form['messages_id']
    if len(comment) > 0:
        query = "INSERT INTO comments (users_id, messages_id, comment, created_at, updated_at) VALUES (:user_id, :messages_id, :comment, NOW(), NOW())"
        data = {
            'user_id': session['id'],
            'comment': comment,
            'messages_id': messages_id,
        }
        mysql.query_db(query, data)
    return redirect('/wall')


app.run(debug=True)
