import sqlite3
import click
from flask import current_app, g
# current_app: request를 handling할 Flask application을 가리킨다.
# g: request시 접근될 데이터들을 저장한다. (db connection정보도 저장)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect( # DATABASE config key(/flaskr/__init__.py)가 가리키는 파일에 연결한다
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row  # 열의 이름으로 접근할 수 있도록 한다.
    return g.db

# 애플리케이션에서 close_db, init_db_command 함수 사용하기 위해 등록
def init_app(app):
    app.teardown_appcontext(close_db)   # return response후에 해당 함수를 호출하도록 설정
    app.cli.add_command(init_db_command)    # flask command로 등록

def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()
        
def init_db():  # db 초기화
    db = get_db()   # db connection 가져오기
    
    with current_app.open_resource('schema.sql') as f:  # 현재 앱에대해서 schema.sql파일을 f변수로 연다
        db.executescript(f.read().decode('utf8'))   # db에 schema.sql 파일 실행

@click.command('init-db')   # 'init-db'라는 명령어 정의
def init_db_command():
    init_db()
    click.echo('Initialized the database.')
