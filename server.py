import hashlib
import sqlite3
import time
from datetime import datetime

from flask import Flask, request

app = Flask(__name__)

conn = sqlite3.connect('server.db', check_same_thread=False)
c = conn.cursor()


def add_user(username, password_hash):
    reg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute(f"INSERT INTO users VALUES ('{reg_date}','{username}','{password_hash}')")
    conn.commit()
    users.append({'registration_date': reg_date, 'username': username, 'password_hash': password_hash})


def create_init_users_table():
    db_users = [('2020-01-23 11:59:46', 'Lina', '01cfcd4f6b8770febfb40cb906715822'),
                ('2020-01-23 12:01:25', 'Alex', '827ccb0eea8a706c4c34a16891f84e7b'),
                ]

    # Create table
    c.execute('''CREATE TABLE users
                 (registration_date text, username text, password_hash text)''')
    # Insert a row of data
    # c.execute("INSERT INTO users VALUES ('2006-01-05 11:59:46','Mary','01cfcd4f6b8770febfb40cb906715822')")
    # c.execute("INSERT INTO users VALUES ('2006-01-05 12:01:25','Jack','827ccb0eea8a706c4c34a16891f84e7b')")
    c.executemany('INSERT INTO users VALUES (?,?,?)', db_users)
    # Save (commit) the changes
    conn.commit()
    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    # conn.close()


def get_hashed_password(pw):
    hasher = hashlib.md5()
    hasher.update(pw.encode(encoding='ANSI'))
    return hasher.hexdigest()


if len(c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()) == 0:
    create_init_users_table()

messages = [
    {'username': 'Jack', 'text': 'Hello!', 'time': time.time()},
    {'username': 'Mary', 'text': 'Hi, Jack', 'time': time.time()},
]
# users = {
#     'Jack': get_hashed_password('12345'),
#     'Mary': get_hashed_password('54321'),
# }

db_users = c.execute('SELECT * FROM users').fetchall()
users = [{'registration_date': u[0], 'username': u[1], 'password_hash': u[2]} for u in db_users]
# for u in db_users:
#     users.append({'registration_date': u[0], 'username': u[1], 'password_hash': u[2]})

print(users)


@app.route("/")
def hello_view():
    return "<h1>Welcome to Python messenger!</h1>"


@app.route("/status")
def status_view():
    """
    Получение статуса сервера
    input: -
    output: {
        "status":bool,
        "time":str,
        "total_users":float,
        "total_messages":float
    }
    """
    return {
        'status': True,
        'time': datetime.now().strftime("%Y.%m.%d %H:%M:%S"),
        'total_users': len(users),
        'total_messages': len(messages)
        # 'time': datetime.now().isoformat()
    }


@app.route("/send", methods=['POST'])
def send():
    """
    Отправка сообщений
    input: {
        "username":str,
        "password": str,
        "text":str
    }
    output: {"ok":bool}
    """
    data = request.json
    username = data['username']
    password = data['password']

    user = next(
        (u for u in users if (u['username'] == username and get_hashed_password(password) == u['password_hash'])), None)
    # if username not in users or users[username] != get_hashed_password(password):
    if user == None:
        return {'ok': False}

    text = data['text']
    messages.append({'username': username, 'text': text, 'time': time.time()})
    print(messages)
    return {'ok': True}


@app.route("/auth", methods=['POST'])
def auth():
    """
    Авторизовать пользователя или сообщить, что пароль неверный
    input: {
        "username":str,
        "password": str
    }
    output: {"ok":bool}
    """
    data = request.json
    username = data['username']
    password = data['password']

    password_hash = get_hashed_password(password)

    if username not in [u['username'] for u in users]:
        add_user(username, password_hash)
        # users[username] = password_hash
        return {'ok': True}
    elif password_hash == next((u['password_hash'] for u in users if u['username'] == username), None):
        return {'ok': True}
    else:
        return {'ok': False}


@app.route("/users")
def users_view():
    """
    Получение списка пользователей
    input: -
    output: {
        "users": [
            {"registration_date": str, "username": str, "password_hash": str},
            ...
        ]
    }
    """
    return {'users': users}
    # return json.dumps(users)


@app.route("/messages")
def messages_view():
    """
    Получение сообщений после отметки after
    input: after - отметка времени
    output: {
        "messages": [
            {"username": str, "text": str, "time": float},
            ...
        ]
    }
    """
    after = float(request.args['after'])

    # new_messages = []
    # for message in messages:
    #     if message['time'] > after:
    #         new_messages.append(message)

    new_messages = [message for message in messages if message['time'] > after]

    return {'messages': new_messages}


app.run()
