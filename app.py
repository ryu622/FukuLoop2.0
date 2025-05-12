import os
from flask import Flask,render_template,request,redirect,url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime,timedelta,date
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import json

# =====================
# インスタンス生成
# =====================
app=Flask(__name__)

# =====================
# Flaskに対する設定
# =====================
import os

# 乱数を設定
app.config['SECRET_KEY']='your_secret_key'
base_dir=os.path.dirname(__file__)
database='sqlite:///'+os.path.join(base_dir,'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI']=database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

# db変数を使用してSQLalchemyを操作できる
db=SQLAlchemy(app)
# Flask_migrateを使用できるようにする
Migrate(app,db)

#ログイン機能追加にお決まりの構文
#@login_requiredで/loginへ飛ばす
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#クッキーによりログインしてきたユーザーを確認
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ===================
# モデル
# ===================
#　課題
class Task(db.Model):
    #テーブル名
    __tablename__='tasks'
    #課題ID
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    #内容
    content=db.Column(db.String(200),nullable=False)
    #完了フラグ
    is_completed=db.Column(db.Boolean,default=False)
    #完了日
    completed_date=db.Column(db.DateTime)
    #復習フラグ（復習するべきか）
    repeat=db.Column(db.Boolean,default=False)
    #表示用
    def __str__(self):
        return f'課題ID：{self.id} 内容：{self.content} 完了フラグ：{self.is_completed}'
    


#ログイン用ユーザー情報
class User(UserMixin,db.Model):
    #テーブル名
    __tablename__='users'
    #ユーザーID
    id=db.Column(db.Integer,primary_key=True)
    #メールアドレス（ユーザーネーム）
    username = db.Column(db.String(80), unique=True, nullable=False)
    #パスワード
    password = db.Column(db.String(200), nullable=False)
    
#完了履歴
class TaskLog(db.Model):
    #履歴id
    id = db.Column(db.Integer, primary_key=True)
    #課題id（外部キー）
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    #完了、未完了、復習完了
    action_type = db.Column(db.String(50), nullable=False)
    #日付ログ
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 関係を定義（TaskテーブルとTaskLogテーブルの関係）
    task = db.relationship('Task', backref=db.backref('logs', lazy=True))


# ==================================================
# ルーティング
# ==================================================

# 一覧
@app.route('/')
@login_required #login必須に
def index():
    #今日を定義しておく 
    now=datetime.utcnow()
    #７日前の日付けを取得
    seven_days_ago = now - timedelta(days=7)
    # 未完了課題を取得
    uncompleted_tasks  = Task.query.filter((Task.is_completed==False)|((Task.completed_date <= seven_days_ago))).all()
    # 完了課題を取得
    completed_tasks  = Task.query.filter_by(is_completed=True).all()
    return render_template('index.html',completed_tasks=completed_tasks,uncompleted_tasks=uncompleted_tasks)

'''#api1
@app.route('/api/uncompleted_tasks')
def uncompleted_tasks():
    #今日を定義しておく 
    now=datetime.utcnow()
    #７日前の日付けを取得
    seven_days_ago = now - timedelta(days=7)
    # 未完了課題を取得
    uncompleted_tasks  = Task.query.filter((Task.is_completed==False)|((Task.completed_date <= seven_days_ago))).all()
    return jsonify({'status': 'ok',
    "message": "取得成功",
    'uncompleted_tasks': uncompleted_tasks
    })

#api2
@app.route('/api/completed_tasks')
def completed_tasks():
    #今日を定義しておく 
    now=datetime.utcnow()
    #７日前の日付けを取得
    seven_days_ago = now - timedelta(days=7)
    # 完了課題を取得
    completed_tasks  = Task.query.filter_by(is_completed=True).all()
    return jsonify({'status': 'ok',
    "message": "取得成功",
    'completed_tasks': completed_tasks
    })
'''
#api3
@app.route('/api/counts')
def api():
    #グラフ表示機能追加
    today = date.today()#今日の日付
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]  # 過去7日
    #日付け,回数の辞書を初期化
    counts = {}  # 空の辞書を用意
    for d in dates:
        counts[d] = 0  # 日付ごとにキーを追加し、値を 0 に設定
    rows = (
        db.session.query(
        func.date(TaskLog.timestamp),
        func.count()
    ).filter((TaskLog.action_type == "completed")|(TaskLog.action_type=="review_completed")
             ).group_by(
        func.date(TaskLog.timestamp)
    ).all())#完了と復習完了を各日付ごとにカウント
    #for文で辞書に格納
    for day_str, count in rows:
        day = date.fromisoformat(day_str)
        counts[day] = count
    print(counts)
    #グラフ生成関数
    '''def generate_graph():
        x = list(counts.keys())  # 日付のリスト
        y = list(counts.values())  # 完了タスク数のリスト
        sns.set()#seabornでグラフのデザインを整える
        plt.figure(figsize=(8,4))
        plt.xlabel('日付',fontname="MS Gothic")
        plt.ylabel('タスクの完了回数(回)',fontname="MS Gothic")
        plt.bar(x,y)
        #保存先の絶対パス
        base_path = os.path.abspath(os.path.dirname(__file__))
        static_path = os.path.join(base_path, 'static', 'graph.png')
        plt.savefig(static_path)#画像を保存
        plt.close()
    generate_graph()'''
    
    
    # 新しい辞書を作成してキーを文字列に変換(countsのキーがdatetimeオブジェクトのため)
    data = {}
    for k, v in counts.items():
        data[k.isoformat()] = v
    
    print(data)
    return jsonify({
    'status': 'ok',
    "message": "取得成功",
    'data': data
})


# 登録
@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_task():
    # POST
    if request.method == 'POST':
        # 入力値取得
        content = request.form['content']
        # インスタンス生成
        task = Task(content=content)
        # 登録
        db.session.add(task)
        db.session.commit()
        # 一覧へ
        return redirect(url_for('index'))
    # GET
    return render_template('new_task.html')

# 完了
@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    # 対象データ取得
    task = Task.query.get(task_id)
    # 完了フラグに「True」を設定
    task.is_completed = True
    #完了日に現在の日付けを登録
    task.completed_date=datetime.utcnow()
    #復習フラグをONに
    task.repeat=True
    #tasklogに追加
    log = TaskLog(task_id=task.id, action_type="completed")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('index'))

# 未完了（戻す）
@app.route('/tasks/<int:task_id>/uncomplete', methods=['POST'])
def uncomplete_task(task_id):
    # 対象データ取得
    task = Task.query.get(task_id)
    # 完了フラグに「False」を設定
    task.is_completed = False
    task.repeat=False
    #tasklogに追加
    log = TaskLog(task_id=task.id, action_type="uncompleted")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('index'))

#新規追加　復習完了ボタン
@app.route('/tasks/<int:task_id>/review_done', methods=['POST'])
def review_done(task_id):
    task = Task.query.get(task_id)
    task.repeat = False
    task.is_completed = True
    #完了日に現在の日付けを登録
    task.completed_date=datetime.utcnow()
    #tasklogに追加
    log = TaskLog(task_id=task.id, action_type="review_completed")
    db.session.add(log)
    db.session.commit()
    return redirect(url_for('index'))

#ログイン機能追加
#forms.pyからインポート
from forms import UserInform
from forms import RegisterForm
#ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    #インスタンス生成
    form = UserInform()
    #バリデーション機能
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(username=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています')
    
    return render_template('login.html', form=form)

#登録処理
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=email).first():
            flash('このユーザー名はすでに使われています')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


#ログアウト
@app.route('/logout')
@login_required
def logout():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=email).first():
            flash('このユーザー名はすでに使われています')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)




# ======================
# 実行
# ======================
if __name__=='__main__':
    app.run(debug=True)           # 登録処理




'''
flask-WTFに修正したため一応コメントアウト
#ログイン
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)  # ← ログイン状態にする！
            next_page = request.args.get('next')  # もともと見ようとしてたページ
            return redirect(next_page or url_for('index'))
        else:
            flash('ユーザー名またはパスワードが間違っています')
    
    return render_template('login.html')

#登録処理
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 同じユーザー名の人がいないか確認
        if User.query.filter_by(username=username).first():
            flash('このユーザー名はすでに使われています')
            return redirect(url_for('register'))

        #データベースに新ユーザー情報を挿入
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('登録が完了しました。ログインしてください。')
        return redirect(url_for('login'))

    else:
        return render_template('register.html')


#ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()  # ← Flask-Loginのログアウト処理
    flash('ログアウトしました')
    return redirect(url_for('login'))
'''