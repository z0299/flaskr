from flask import(
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flaskr.db import get_db
from flaskr.auth import login_required
from werkzeug.exceptions import abort

# 'blog'라는 이름의 blueprint 생성
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    # jinja 템플릿 주소와 필요한 변수 넘겨주기
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Content is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for("index"))
    return render_template('blog/create.html')

# update와 delete모두 게시물 작성자와 로그인한 유저가 같은지 확인해야 한다.\
# 따라서 해당 작동함수를 만들어두고 가져다 쓰자.
def get_post(id, check_author=True):
    post = get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ?", (id,)
    ).fetchone()
    
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post['author_id'] != g.user['id']:
        abort(403)  # Forbidden
    
    return post

# 업데이트
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id): # id 변수를 받는다.
    post = get_post(id)
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None
        
        if not title:
            error = 'Title is required.'
        if not body:
            error = 'Content is required.'
            
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?",
                (title, body, id)
            )
            db.commit()
            return redirect(url_for("index"))
        
    return render_template('blog/update.html', post=post)

# 삭제
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for("index"))