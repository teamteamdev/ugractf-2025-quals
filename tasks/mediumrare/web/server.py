from cryptography.fernet import Fernet
from flask import abort, Flask, make_response, redirect, render_template, request, url_for
import json
import html
from html.parser import HTMLParser
from kyzylborda_lib.secrets import get_flag, get_secret, validate_token
import os
import re
import secrets
import sqlite3


app = Flask(__name__)
cursors = {}

def get_cursor(token: str):
    if token in cursors:
        return cursors[token]

    con = sqlite3.connect(f"/state/{token}.db", autocommit=True)
    cur = con.cursor()
    cursors[token] = cur
    cur.execute("PRAGMA journal_mode=WAL")
    return cur


@app.route("/<token>/")
def list_articles(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    cur = get_cursor(token)
    res = cur.execute("SELECT id, title FROM article")
    rows = res.fetchall()

    articles = [{"id": row[0], "title": row[1]} for row in rows[::-1]]

    return render_template("list.html", articles=articles)


@app.route("/<token>/<id>/")
def view(token: str, id: str):
    if not validate_token(token):
        return "Invalid token.", 401

    if "password" in request.args:
        response = redirect(url_for("view", token=token, id=id), code=303)
        response.set_cookie("password", request.args["password"], path=f"/{token}/{id}", max_age=2147483647)
        return response

    if id.isalnum():
        row = get_cursor(token).execute(f"SELECT title, free_content, paid_content FROM article WHERE id = '{id}'").fetchone()
    else:
        row = None

    if row is None:
        title = "Кто здесь?"
        content = "<p>Такой страницы нет. Хотите, чтобы была &mdash; <a href='new'>напишите статью сами</a>.</p>"
    else:
        title, content, paid_content = row
        if paid_content:
            if "password" in request.cookies:
                try:
                    content += Fernet(request.cookies["password"]).decrypt(paid_content).decode()
                except Exception:
                    return "Failed to decrypt paid content", 401
            else:
                content += "<div class='ce-paid-content-delimiter'></div>"

    return render_template("view.html", title=title, content=content)


@app.route("/<token>/new/", methods=["GET"])
def new_get(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    return render_template("new.html")


@app.route("/<token>/new/", methods=["POST"])
def new_post(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    id = secrets.token_hex(16)
    title = request.form["title"]
    free_content = sanitize_html(request.form["free_content"])
    paid_content = sanitize_html(request.form["paid_content"])

    password = Fernet.generate_key().decode()
    if paid_content:
        paid_content = Fernet(password).encrypt(paid_content.encode()).decode()

    cur = get_cursor(token)
    try:
        cur.execute(f"INSERT INTO article(id, title, free_content, paid_content) VALUES ('{id}', '{title}', '{free_content}', '{paid_content}')")
    except sqlite3.OperationalError:
        return "SQL error", 500

    response = make_response(render_template("posted.html", token=token, id=id, password=password))
    response.set_cookie("password", password, path=f"/{token}/{id}", max_age=2147483647)
    return response


@app.route("/<token>/contest/", methods=["POST"])
def contest(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    url = request.form["url"]

    if url.startswith("http"):
        os.makedirs("/state/markers", exist_ok=True)
        with open(os.path.join(f"/state/markers/{token}"), "w") as f:
            f.write(url)

    return render_template("submitted.html")


@app.route("/<token>/__reset_db__/", methods=["POST"])
def reset_db(token: str):
    if not validate_token(token):
        return "Invalid token.", 401

    flag = get_flag(token)

    title = 'Poster v2: что нового?'
    free_content = '''
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    Мы, команда разработки Poster, следим не только за удобством, но и за безопасностью нашего сервиса. Приватность журналистов и уменьшение фейков в медиа стоят для нас на первом месте. Взлом Poster, случившийся год назад, показал, что эта задача далеко не так проста, как кажется. Потому за последний год мы приняли меры по увеличению безопаности сайта для предотвращения подобных ситуаций в будущем.
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <ol class="cdx-block cdx-list cdx-list--ordered">
                    <li class="cdx-list__item">
                        Внутреннее расследование показало, что главной причиной, по которой взлом Poster оказался возможен — подход старой команды к продукту. Мы провели интервью со всеми разработчиками, уволили несколько некомпетентных программистов и взамен набрали людей с сертификатами. Большинство из них — молодые студенты, понравившиеся оставшейся команде и быстро втянувшиеся в процесс разработки. С остальными провели курс повышения квалификации.
                    </li>
                    <li class="cdx-list__item">
                        Провели аудит кода и решили переписать продукт с нуля. Функциональность и интефрейс при этом по большей части не изменились, так что редакторам и читателям волноваться не о чем.
                    </li>
                    <li class="cdx-list__item">
                        Выпилили поддержку сырого HTML. Эта функция часто использовалась для взломов, не была регулируема и доставляла проблемы неопытным редакторам.
                    </li>
                    <li class="cdx-list__item">
                        Убрали редко используемую функцию — чеклисты. Согласно нашей статистике, они использовались меньше, чем в 2% постов, но при этом значительно усложняли код, потенциально содержащий опасные баги. Списки оставили на месте.
                    </li>
                    <li class="cdx-list__item">
                        Посты теперь нельзя редактировать: после публикации тексты статей неизменны. Это упростило процесс модерации, уменьшило потенциальные последствия от взломов, а также упростило авторизацию.
                    </li>
                    <li class="cdx-list__item">
                        Включили шифрование постов. Текст под пейволлом теперь хранится в базе зашифрованным и расшифровывается только при запросах пользователей с подпиской. Даже злоумышленники, получившие доступ к базе данных, не смогут прочитать ваши статьи целиком.
                    </li>
                </ol>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <h2 class="ce-header">
                    Это ещё не всё!
                </h2>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    В честь новой юбилейной версии Poster мы объявляем конкурс статей. Требования очень простые:
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <ol class="cdx-block cdx-list cdx-list--ordered">
                    <li class="cdx-list__item">
                        Рекомендуемый объём — от 350 слов.
                    </li>
                    <li class="cdx-list__item">
                        Статью нужно писать самостоятельно. Не допускается списывание статьи или ее фрагментов из какого-либо источника или воспроизведение по памяти чужого текста.
                    </li>
                    <li class="cdx-list__item">
                        Допускается прямое или косвенное цитирование с обязательной ссылкой на источник (ссылка даётся в свободной форме). Объём цитирования не должен превышать объём Вашего собственного текста.
                    </li>
                </ol>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    Продумайте композицию статьи. Соблюдайте речевые и орфографические нормы.
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    При оценке статьи особое внимание уделяется соблюдению требований объёма и самостоятельности написания сочинения и умениям аргументировать позицию.
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    Не забудьте указать в статье контакты для обратной связи.
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    Ссылку на статью, опубликованную на Poster, отправьте в форму:
                </div>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <form action="../contest/" method="POST" style="margin: 0.5rem 0;">
                    <input style="box-sizing: border-box; width: 100%; font: inherit; padding: 0.5rem 0.75rem; outline: none; border: 0.125rem solid #2ea0ff; border-radius: 0.25rem;" name="url" placeholder="URL">
                </form>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <h2 class="ce-header">
                    Подарок
                </h2>
            </div>
        </div>
        <div class="ce-block">
            <div class="ce-block__content">
                <div class="ce-paragraph cdx-block">
                    Спасибо, что остаётесь с нами! Хотите видеть больше обновлений и постов? Поддержите нас, порекомендовав знакомым или купив локальную версию Poster задёшево с промокодом:
                </div>
            </div>
        </div>
    '''
    free_content = re.sub(r"\s{2,}", "", free_content.strip())
    paid_content = f'<div class="ce-block"><div class="ce-block__content"><div class="ce-paragraph cdx-block"><b>{flag}</b></div></div></div>'

    password = get_secret("admin_password", token)
    paid_content = Fernet(password).encrypt(paid_content.encode()).decode()

    id = get_secret("writeup_id", token)

    cur = get_cursor(token)

    cur.execute("DROP TABLE IF EXISTS article")
    cur.execute("CREATE TABLE article(id, title, free_content, paid_content)")
    cur.execute(f"INSERT INTO article(id, title, free_content, paid_content) VALUES ('{id}', '{title}', '{free_content}', '{paid_content}')")

    return "The database has been reset."


ALLOWED_TAGS = ("b", "i", "strong", "em", "u", "mark", "code", "a", "h1", "h2", "h3", "h4", "h5", "h6", "div", "p", "textarea", "ol", "ul", "li")

class HTMLSanitizer(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sanitized_html = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str]]):
        if tag not in ALLOWED_TAGS:
            return
        self.sanitized_html += f"<{tag}"
        for name, value in attrs:
            if name in ("class", "disabled") or (name == "href" and value.startswith("http")):
                self.sanitized_html += f" {name}=\""
                self.sanitized_html += html.escape(value)
                self.sanitized_html += "\""
        self.sanitized_html += ">"

    def handle_endtag(self, tag: str):
        if tag in ALLOWED_TAGS:
            self.sanitized_html += f"</{tag}>"

    def handle_data(self, data: str):
        self.sanitized_html += html.escape(data)


def sanitize_html(html: str) -> str:
    parser = HTMLSanitizer()
    parser.feed(html)
    parser.close()
    return parser.sanitized_html
