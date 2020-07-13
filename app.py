from flask import Flask
import sqlite3
from flask import g
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'spotify'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


def connect_db():
    return mysql.connect()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


@app.route('/api/v1.0/', methods=['GET'])
def hello_world():
    # data = {'username': 'ali'}
    # response = app.response_class(
    #     response=json.dumps(data),
    #     status=200,
    #     mimetype="application/json"
    # )
    # response = query_db('select * from users')
    return 'test'


def query_db(query, args=(), one=False):
    cur = g.db.cursor()
    cur.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv


if __name__ == '__main__':
    app.run()
