from flask import Flask

from datetime import datetime
from flask import request, render_template
import redis

app = Flask(__name__)
app.config.from_object('config')

# создаем базу данных
db = redis.StrictRedis(host=app.config['DB_HOST'], port=app.config['DB_PORT'], db=app.config['DB_NO'])


# связывает url и эту функцию;
# метод GET посылает данные на сервер, метод  POST используется для отправления данных HTML-формы на сервер
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['submission']  # получаем текст из формы
        if len(text) < 1:
            return render_template('index.html',
                                   history=get_posts())  # подставляем значение history в index.html (в шаблон)
        post_id = str(db.incr("id"))
        # добавляем информацию о посте в базу данных
        db.hmset('post:' + post_id, dict(date_time=datetime.strftime(datetime.now(), "%d.%m.%Y %H:%M:%S"), text=text))
        # добавляем id в список
        db.lpush('history:', str(post_id))
        return render_template('index.html', history=get_posts())
    return render_template('index.html', history=get_posts())


def get_posts():
    posts = db.lrange('history:', 0, -1)  # сортировка постов в обратном порядке
    history = []
    for post_id in posts:
        post = db.hgetall('post:' + str(post_id, 'utf-8'))  # получение информации по id
        history.append(dict(date_time=post[b'date_time'].decode(), text=post[b'text'].decode()))
    return history
