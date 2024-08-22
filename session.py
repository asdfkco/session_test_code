from flask import Flask, session, redirect, url_for, request, make_response
from datetime import timedelta
from markupsafe import escape
import os
import uuid

app = Flask(__name__)

# 세션 유지 시간을 3분으로 설정(테스트를 위해 3분으로 지정)
app.permanent_session_lifetime = timedelta(minutes=3)

# 쿠키에 저장할 key와 세션 데이터 저장 경로 설정
COOKIE_KEY = 'session_key'
SESSION_FILE = 'session_data.txt'

# session의 정보가 있는 txt파일을(database 대용) 삭제하여 내림
def delete_session_file():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# database 대용으로 사용한 txt 파일로 session의 정보를 저장
def save_session_to_file(session_key):
    with open(SESSION_FILE, 'w') as f:
        # 세션 key를 포함한 모든 key:value 쌍을 파일에 저장
        f.write(f'session_key:{session_key}\n')
        for key, value in session.items():
            f.write(f'{key}:{value}\n')

# 새로고침 시에 session을 유지하기 위해 cookie에서 가져온 session key값
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
    # 쿠키에서 세션 key를 가져오고 세션 txt(database 대용) 파일에서 불러오기 시도
    session_key = request.cookies.get(COOKIE_KEY)
    if session_key:
        load_session_from_file(session_key)

    # 세션에서 'username'을 가져와 h2 태그로 표시
    if 'username' in session:
        username = session['username']
        # ip를 구분하기 위하여 각각 .25, .74 서버에 배포하였습니다.
        return f'<h2>192.168.200.74 Hello, {escape(username)}!</h2>'
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #form 데이터로 넘어온 값을 session에 저장
        session['username'] = request.form['username']

        # 생성된 세션에 대한 랜덤 key를 쿠키에 저장
        session_key = str(uuid.uuid4())
        resp = make_response(redirect(url_for('index')))
        resp.set_cookie(COOKIE_KEY, session_key)
        
        save_session_to_file(session_key)  # 세션 데이터를 파일에 저장
        return resp
        
    # ip를 구분하기 위하여 각각 .25, .74 서버에 배포하였습니다.
    return '''
        <h3>192.168.200.74</h3>
        <form method="post">
            <p><input type="text" name="username" placeholder="Enter your username">
            <p><input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
def logout():
    # 세션에서 'username'을 제거
    session.pop('username', None)
    
    # 쿠키에서 세션 key를 제거
    resp = make_response(redirect(url_for('index')))
    resp.set_cookie(COOKIE_KEY, '', expires=0)
    
    delete_session_file()  # 세션 파일 삭제
    return resp

if __name__ == '__main__':
    # 0.0.0.0:5000으로 애플리케이션 실행 (외부에서도 접근 가능)
    app.run(host='0.0.0.0', port=5000, debug=True)  

