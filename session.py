from flask import Flask, session, redirect, url_for, request, make_response
from datetime import timedelta
from markupsafe import escape
import os
import uuid

app = Flask(__name__)

app.permanent_session_lifetime = timedelta(minutes=3)

COOKIE_KEY = 'session_key'
SESSION_FILE = 'session_data.txt'
def delete_session_file():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

def save_session_to_file(session_key):
    with open(SESSION_FILE, 'w') as f:
        f.write(f'session_key:{session_key}\n')
        for key, value in session.items():
            f.write(f'{key}:{value}\n')

def load_session_from_file(session_key):
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            lines = f.readlines()
            stored_key = lines[0].strip().split(':', 1)[1]
            if stored_key == session_key:
                for line in lines[1:]:
                    key, value = line.strip().split(':', 1)
                    session[key] = value

@app.route('/')
def index():
    session_key = request.cookies.get(COOKIE_KEY)
    if session_key:
        load_session_from_file(session_key)

    if 'username' in session:
        username = session['username']
        return f'<h2>192.168.200.74 Hello, {escape(username)}!</h2>'
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']

        session_key = str(uuid.uuid4())
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie(COOKIE_KEY, session_key)
        
        save_session_to_file(session_key) 
        return resp
        
    return '''
        <h3>192.168.200.74</h3>
        <form method="post">
            <p><input type="text" name="username" placeholder="Enter your username">
            <p><input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
def logout():
    session.pop('username', None)
    
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(COOKIE_KEY, '', expires=0)
    
    delete_session_file()  
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  

