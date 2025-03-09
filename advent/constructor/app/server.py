from flask import abort, Flask, render_template
import sqlite3


app = Flask(__name__)

con = sqlite3.connect("/tmp/constructor.db")
cur = con.cursor()


@app.errorhandler(404)
def page_not_found(e):
    return render_template("post.html", title="Здесь ничего нет", content="<p>Проходите мимо</p>"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("post.html", title="Вы уронили сервер", content="<p>Больше так не делайте</p>"), 500


@app.route("/")
def home():
    title, content = cur.execute("SELECT ЗАГОЛОВОК, СОДЕРЖИМОЕ FROM ОЧЕРКИ WHERE №_ПО_ПОРЯДКУ = 1").fetchone()
    return render_template("post.html", title=title, content=content)


@app.route("/ОЧЕРКИ/<n>/")
def post(n):
    try:
        post = cur.execute("SELECT ЗАГОЛОВОК, СОДЕРЖИМОЕ FROM ОЧЕРКИ WHERE №_ПО_ПОРЯДКУ = " + n).fetchone()
    except sqlite3.OperationalError:
        abort(500)
    if post is None:
        abort(404)
    else:
        title, content = post
        return render_template("post.html", title=title, content=content)
