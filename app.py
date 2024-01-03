from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    intro = db.Column(db.String(300), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class PL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), nullable=False)
    passwords = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<PL %r>' '<Article %r>' % self.id


@app.route('/')
@app.route('/home')
def index():
    return render_template("main.html")


@app.route('/2')
@app.route('/home2')
def index2():
    return render_template("base2.html")


@app.route('/about')
def about():
    return render_template("About.html")


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template("posts.html", articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template("post_detail.html", article=article)


@app.route('/posts/<int:id>/delete')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except db.DoesNotExist:
        return "При удалении статьи произошла ошибка"


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
def post_update(id):
    article = Article.query.get(id)
    if request.method == "POST":
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        try:
            db.session.commit()
            return redirect('/posts')
        except db.DoesNotExist:
            return "При редактировании статьи произошла ошибка"
    else:
        return render_template("post_update.html", article=article)


@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        article = Article(title=title, intro=intro, text=text)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except db.DoesNotExist:
            return "При добавлении статьи произошла ошибка"
    else:
        return render_template("create-article.html")


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == "POST":
        name = request.form['name']
        login = request.form['login']
        email = request.form['email']
        passwords = request.form['passwords']

        existing_user = PL.query.filter_by(login=login).first()
        existing_email = PL.query.filter_by(email=email).first()

        if existing_user:
            return "Пользователь с таким логином уже существует"
        elif existing_email:
            return "Пользователь с таким адресом электронной почты уже существует"
        else:
            pl = PL(name=name, login=login, email=email, passwords=passwords)
            db.session.add(pl)
            db.session.commit()
            return redirect('/login')
    else:
        return render_template("registration.html")


@app.route('/login', methods=['POST', 'GET'])
def login_check():
    if request.method == "POST":
        login = request.form['login']
        passwords = request.form['passwords']
        pl = PL.query.filter_by(login=login).first()
        if pl:
            if pl.passwords == passwords:
                return redirect('/home2')
            else:
                return "Неверный пароль"
        else:
            return "Пользователь не найден"
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
