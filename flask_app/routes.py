# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
from flask import current_app as app
from flask import render_template, redirect, request, session, url_for, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from .utils.database.database  import database
from werkzeug.datastructures   import ImmutableMultiDict
from pprint import pprint
import json
import random
import functools
from . import socketio
from flask_app import socketio 

db = database()


#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "email" not in session:
            return redirect(url_for("login", next=request.url))
        return func(*args, **kwargs)
    return secure_function

def getUser():
	return session['email'] if 'email' in session else 'Unknown'

@app.route('/login')
def login():
    session.pop('email', default=None)
    return render_template('login.html', user="Unknown")

@app.route('/logout')
def logout():
	session.pop('email', default=None)
	return redirect('/home')

@app.route('/processlogin', methods=['POST'])
def process_login():
    email = request.form.get('email')
    password = request.form.get('password')
    new_user = request.form.get('new_user') == 'true'

    existing_user = db.query("SELECT * FROM users WHERE email = %s", (email,))
    if existing_user:
        stored_password = existing_user[0].get('password')
        if stored_password:
            # Treat as returning user even if they checked 'new user'
            new_user = False

    if new_user:
        result = db.createUser(email=email, password=password)
        if result.get('success') == 0:
            return json.dumps({'success': 0, 'message': result.get('message', 'Failed to create user')})
    else:
        encrypted = db.onewayEncrypt(password)
        user = db.query("SELECT * FROM users WHERE email = %s AND password = %s", (email, encrypted))
        if not user:
            return json.dumps({'success': 0, 'message': 'Invalid email or password'})

    session['email'] = email
    return json.dumps({'success': 1})

	
#######################################################################################
# CHATROOM RELATED
#######################################################################################
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=getUser())

# When someone joins
@socketio.on('join')
def handle_join(data):
    username = data['user']
    emit(data)
    emit('status', f"{username} has entered the room.", broadcast=True)

# When a message is sent
@socketio.on('message')
def handle_message(data):
    emit('message', {
        'user': data['user'],
        'text': data['text']
    }, broadcast=True)

# When someone leaves
@socketio.on('leave')
def handle_leave(data):
    username = data['user']
    emit('status', f"{username} has left the room.", broadcast=True)

#######################################################################################
# OTHER
#######################################################################################
@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	print(db.query('SELECT * FROM users'))
	x     = random.choice(['I played DIII soccer at Kalamazoo College my freshman year',
							'I have 2 dogs.',
                            'I am a MSU CSE graduate.', 
                            'I love baking (speficially cookies)',
                            'I spend as much time as I can outside.'])
	return render_template('home.html', fun_fact = x, user=getUser())

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route('/projects')
def projects():
	return render_template('projects.html', user=getUser())

@app.route('/piano')
def piano():
	return render_template('piano.html', user=getUser())

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)
	return render_template('resume.html', resume_data = resume_data, user=getUser())


@app.route('/users')
def users():
    users = db.query("SELECT email, user_id FROM users")

    return render_template('users.html', users=users)