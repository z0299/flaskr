# flaskr 디렉토리가 package로써 동작한다는 것을 알려주는 파일
import os
from flask import Flask

def create_app(test_config=None):   # application factory function
    # 앱을 생성
    app = Flask(__name__, instance_relative_config=True)    # Flask instance 생성
    # __name__: 현재 파이썬 모듈 이름
    # instance_relative_config: config 파일이 instance folder에 있다는 것을 알린다. 
    app.config.from_mapping( # default configuration 설정
        SECRET_KEY='dev',   # 데이터를 안전하게 보관하기위해 랜덤값으로 설정해야 한다
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),  # SQLite DB파일이 저장될 경로 지정 -> app.instance_path에 flaskr.sqlite라는 이름으로 저장
        # app.instance_path는 플라스크에서 instance folder로 지정한 경로이다.
    )
    
    if test_config is None:
        # testing이 아닐 때 instance config을 로드
        app.config.from_pyfile('config.py', silent=True)    # default configuration을 가져온다 (deploy시)
    else:
        # test config 로드
        app.config.from_mapping(test_config)
    
    # instance folder가 존재하도록 한다    
    try:
        os.makedirs(app.instance_path)  # app.instance_path에 SQLite DB파일이 저장되도록 생성
    except OSError:
        pass
    
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    # db initialize factory에 등록
    from . import db
    db.init_app(app)
    
    # 'auth' blueprint factory에 등록
    from . import auth
    app.register_blueprint(auth.bp)
    
    # 'blog' blueprint factory에 등록
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')
    # flaskr 앱은 메인 화면이 블로그 글화면이기 때문에 '/' URL을 index로 등록한다
    # url_rule에 의해 url_for('index') 와 url_for('blog.index') 모두 허용한다. (blog prefix를 등록하지 않았기 때문)
    
    return app