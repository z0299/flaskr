import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# 'auth'라는 이름의 blueprint 생성
bp = Blueprint('auth', __name__, url_prefix='/auth')
# url_prefix: 'auth' blueprint와 관련된 URL들은 prefix로 /auth라는 값을 가지게 될 것이다.

@bp.route('/register', methods=('GET', 'POST')) # 사용자가 /auth/register로 들어올 때 register view function을 뿌려준다.
def register():
    # 유저 생성
    if request.method == 'POST':    # 사용자가 form을 제출하면 'POST'로 값이 들어온다
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        
        # 사용자 이름이나 비밀번호가 없는 경우
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        
        # 에러가 없으면 ...
        if error is None:
            try:
                # 사용자 생성
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",  # ?: placeholder (user input)
                    (username, generate_password_hash(password)),   # password는 보안을 위해 hash로 바꿔서 저장한다
                )
                db.commit() # 변경사항을 저장 (트랜잭션 종료)
            # 무결성 에러 - username이 사용중인 경우
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # 회원가입이 완료되면 login 페이지로 redirect 해준다
                return redirect(url_for("auth.login"))  # url_for가 login view에 대한 URL을 생성해준다.
        
        # flask에서 사용자에게 피드백을 주는 방식. -> 레이아웃 템플릿과 결합하여 사용
        flash(error)
    
    # 회원가입 실패시 회원가입 화면을 다시 띄워준다.
    return render_template('auth/register.html')    # html template를 render

# 'login'이라는 이름의 blueprint 생성
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()    # 하나의 row만을 가져온다
        
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):   # 저장할 때 진행했던 해시방식으로 해시 값을 풀어 비교한다
            error = 'Incorrect password.'
        
        # validation에 성공하면 ...
        if error is None:
            session.clear() # db에 세션정보를 저장
            session['user_id'] = user['id'] # user id를 새 세션에 저장한다
            # 쿠키와 세션의 차이?
            # 쿠키: 사용자 정보에 대한 내용을 사용자의 로컬 컴퓨터나 메모리에 파일로 저장한 것
            # 세션: 사용자 정보를 브라우저의 서버 DB에 저장한다 (브라우저 종료시 사라진다) / 사용자는 세션id를 쿠키로 저장한다.
            return redirect(url_for('index'))
        
        flash(error)
        
    return render_template('auth/login.html')

@bp.before_app_request  # every request 이전에 일어날 일 (=before_request 함수)
def load_logged_in_user():  # session에 user_id가 저장되어있는지 확인
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id, )
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear() # logout하면 세션에서 user id정보 제거
    return redirect(url_for('index'))

# 블로그 포스트를 생성, 수정, 삭제 시 로그인상태여야 한다. 로그인 여부 확인하는 함수
def login_required(view):
    @functools.wraps(view)  # decorator - 새 함수를 불러올 때 기존 함수의 정보를 가지고 들어가도록 한다
    # decorator는 original view를 감싸고있는 new view를 뿌려준다.
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view