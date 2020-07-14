from flask import Flask
from flask import jsonify
from flask_mysqldb import MySQL
from flask import request
import datetime

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'spotify'
mysql = MySQL(app)


@app.route('/api/v1.0/user_likes_music/<int:user_id>/<int:music_id>', methods=['GET'])
def user_likes_music(user_id, music_id):
    response = cud_query_db("INSERT INTO user_likes_music (user_id,music_id) VALUES (%s,%s)", (user_id, music_id))
    return response


@app.route('/api/v1.0/user_unlikes_music/<int:user_id>/<int:music_id>', methods=['GET'])
def user_unlikes_music(user_id, music_id):
    response = cud_query_db("DELETE FROM user_likes_music WHERE user_id = %s AND music_id = %s", (user_id, music_id))
    return response


@app.route('/api/v1.0/user_follows/<int:first_user_id>/<int:second_user_id>', methods=['GET'])
def user_follow(first_user_id, second_user_id):
    response = cud_query_db("INSERT INTO user_follows (firstuser_id,seconduser_id) VALUES (%s,%s)",
                            (first_user_id, second_user_id))
    return response


@app.route('/api/v1.0/user_follows/<int:user_id>/<int:music_id>', methods=['GET'])
def user_unfollow(first_user_id, second_user_id):
    response = cud_query_db("DELETE FROM user_follows WHERE firstuser_id = %s AND seconduser_id = %s",
                            (first_user_id, second_user_id))
    return response


@app.route('/api/v1.0/get_user/username=<username>&email=<email>/', methods=['GET'])
def get_user_data(username, email):
    response = read_query_db("SELECT * FROM listener WHERE username = (%s) AND email = (%s)",
                             (username, email))
    return response


@app.route('/api/v1.0/user_plays_music/<int:user_id>/<int:music_id>', methods=['GET'])
def user_plays_music(user_id, music_id):
    now = datetime.datetime.utcnow()
    response = cud_query_db("INSERT INTO user_plays_music (user_id,music_id,music_date_time_played) VALUES (%s,%s,%s)",
                            (user_id, music_id, now.strftime('%Y-%m-%d %H:%M:%S')))
    return response


@app.route('/api/v1.0/user_login', methods=['POST'])
def user_login():
    data = request.get_json()
    username = data.get('username', '')
    return username


@app.route('/api/v1.0/user_sign_up', methods=['POST'])
def user_signup():
    data = request.get_json()
    username = data.get('username', '')
    return username


@app.route('/api/v1.0/remember_password', methods=['POST'])
def user_remember_password():
    data = request.form
    username = data.get('username')
    return username


def read_query_db(query, args=()):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, args)
        columns = cur.description
        rv = [{columns[index][0]: column for index, column in enumerate(value)} for value in cur.fetchall()]
        mysql.connection.commit()
        cur.close()
        if cur.rowcount <= 0:
            return jsonify(status="failed",
                           code=201,
                           message="No data found!")
        else:
            return jsonify(status="success",
                           code=200,
                           message="edited!",
                           content=rv)
    except Exception as e:
        cur.close()
        return jsonify(status="failed",
                       code=201,
                       message=str(e))


def cud_query_db(query, args=()):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, args)
        mysql.connection.commit()
        cur.close()
        return jsonify(status="success",
                       code=200,
                       message="done!")
    except Exception as e:
        cur.close()
        return jsonify(status="failed",
                       code=201,
                       message=str(e))


if __name__ == '__main__':
    app.run()
