from flask import Flask
from flask import jsonify
from flask_mysqldb import MySQL
from flask import request
import datetime
from flask_bcrypt import Bcrypt
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'spotify'
mysql = MySQL(app)
bcrypt = Bcrypt()


@app.route('/api/v1.0/user_likes_music/<int:user_id>/<int:music_id>', methods=['GET'])
def user_likes_music(user_id, music_id):
    now = datetime.datetime.utcnow()
    response = cud_query_db("INSERT INTO user_likes_music (user_id,music_id) VALUES (%s,%s)", (user_id, music_id))
    playlist_id = read_field_query_db("SELECT id FROM playlist WHERE title = (%s)",
                                      ("Liked Songs",))
    add_to_liked_playlist = cud_query_db(
        "INSERT INTO playlist_has_music (playlist_id,music_id,user_id,music_added_date) VALUES (%s,%s,%s,%s)",
        (playlist_id, music_id, user_id, now.strftime('%Y-%m-%d')))
    return add_to_liked_playlist


@app.route('/api/v1.0/user_unlikes_music/<int:user_id>/<int:music_id>', methods=['GET'])
def user_unlikes_music(user_id, music_id):
    response = cud_query_db("DELETE FROM user_likes_music WHERE user_id = %s AND music_id = %s", (user_id, music_id))
    playlist_id = read_field_query_db("SELECT id FROM playlist WHERE title = (%s)",
                                      ("Liked Songs",))
    delete_from_liked_playlist = cud_query_db(
        "DELETE FROM playlist_has_music WHERE playlist_id= %s AND music_id = %s AND user_id = %s",
        (playlist_id, music_id, user_id))
    return delete_from_liked_playlist


@app.route('/api/v1.0/user_likes_playlist/<int:user_id>/<int:playlist_id>', methods=['GET'])
def user_likes_playlist(user_id, playlist_id):
    response = cud_query_db("INSERT INTO user_likes_playlist (user_id,playlist_id) VALUES (%s,%s)",
                            (user_id, playlist_id))
    add_to_shares_playlist = cud_query_db(
        "INSERT INTO user_shares_playlist (user_id,playlist_id) VALUES (%s,%s)",
        (user_id, playlist_id,))
    return add_to_shares_playlist


@app.route('/api/v1.0/user_unlikes_playlist/<int:user_id>/<int:playlist_id>', methods=['GET'])
def user_unlikes_playlist(user_id, playlist_id):
    response = cud_query_db("DELETE FROM user_likes_playlist WHERE user_id = %s AND playlist = %s",
                            (user_id, playlist_id))
    delete_from_shares_playlist = cud_query_db(
        "DELETE FROM user_shares_playlist WHERE playlist_id= %s AND user_id = %s",
        (playlist_id, user_id))
    return delete_from_shares_playlist


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
    response = cud_query_db(
        "INSERT INTO user_plays_music (user_id,music_id,music_date_played,music_time_played) VALUES (%s,%s,%s,%s)",
        (user_id, music_id, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S')))
    return response


@app.route('/api/v1.0/user_add_music_to_playlist/<int:playlist_id>/<int:music_id>/<int:user_id>', methods=['GET'])
def user_add_music_to_playlist(playlist_id, music_id, user_id):
    now = datetime.datetime.utcnow()
    response = cud_query_db(
        "INSERT INTO playlist_has_music (playlist_id,music_id,user_id,music_added_date) VALUES (%s,%s,%s,%s)",
        (playlist_id, music_id, user_id, now.strftime('%Y-%m-%d')))
    return response


@app.route('/api/v1.0/user_delete_music_from_playlist/<int:playlist_id>/<int:music_id>/<int:user_id>', methods=['GET'])
def user_delete_music_from_playlist(playlist_id, music_id, user_id):
    response = cud_query_db(
        "DELETE FROM playlist_has_music WHERE  playlist_id = (%s) AND music_id = (%s) AND user_id = (%s)",
        (playlist_id, music_id, user_id,))
    return response


@app.route('/api/v1.0/user_add_playlist/<int:user_id>/<title>', methods=['GET'])
def user_add_playlist(user_id, title):
    now = datetime.datetime.utcnow()
    response1 = cud_query_db(
        "INSERT INTO playlist(title,last_update,created_date) VALUES (%s,%s,%s)",
        (title, now.strftime('%Y-%m-%d'), now.strftime('%Y-%m-%d')))
    playlist_id = read_field_query_db("SELECT id FROM playlist WHERE title = (%s)",
                                      (title,))
    response2 = cud_query_db(
        "INSERT INTO user_creates_playlist(user_id,playlist_id,created_date) VALUES (%s,%s,%s)",
        (user_id, playlist_id, now.strftime('%Y-%m-%d')))
    response3 = cud_query_db(
        "INSERT INTO user_shares_playlist(user_id,playlist_id) VALUES (%s,%s)",
        (user_id, playlist_id))
    return response3


@app.route('/api/v1.0/user_shares_playlist/<int:playlist_id>/<int:user_id>', methods=['GET'])
def user_shares_playlist(user_id, playlist_id):
    response3 = cud_query_db(
        "INSERT INTO user_shares_playlist(user_id,playlist_id) VALUES (%s,%s)",
        (user_id, playlist_id))
    return response3


@app.route('/api/v1.0/user_update_playlist/<old_title>/<new_title>', methods=['GET'])
def user_update_playlist(old_title, new_title):
    now = datetime.datetime.utcnow()
    playlist_id = read_field_query_db("SELECT id FROM playlist WHERE title = (%s)",
                                      (old_title,))
    response = cud_query_db(
        "UPDATE playlist SET title = (%s),last_update = (%s) WHERE id = (%s)",
        (new_title, now.strftime('%Y-%m-%d'), playlist_id))
    return response


@app.route('/api/v1.0/user_delete_music_from_album/<int:album_id>/<int:music_id>', methods=['GET'])
def user_delete_music_from_album(album_id, music_id):
    response = cud_query_db(
        "DELETE FROM music WHERE  album_id = (%s) AND music_id = (%s)",
        (album_id, music_id,))
    return response


@app.route('/api/v1.0/user_delete_music_from_album/<int:album_id>', methods=['GET'])
def user_delete_album(album_id):
    #TODO
    response = cud_query_db(
        "DELETE FROM album WHERE  album_id = (%s)",
        (album_id,))
    return response


@app.route('/api/v1.0/user_report_music_to_admin/<int:music_id>', methods=['GET'])
def user_report_music_to_admin(music_id):
    response = cud_query_db(
        "INSERT INTO reported_music (reportedmusic_id) VALUES (%s)",
        (music_id,))
    return response


@app.route('/api/v1.0/get_user_playlists/<int:user_id>', methods=['GET'])
def get_user_playlists(user_id):
    response = read_query_db("SELECT * FROM user_shares_playlist WHERE user_id = (%s)",
                             (user_id,))
    return response


@app.route('/api/v1.0/user_plays_music_number/<int:user_id>/<int:music_id>', methods=['GET'])
def user_plays_music_number(user_id, music_id):
    response = read_field_query_db(
        "SELECT COUNT(*) FROM user_plays_music WHERE user_id = (%s) AND music_id = (%s) AND music_date_played BETWEEN CURDATE() - INTERVAL 1 DAY AND CURDATE()",
        (user_id, music_id))
    return response


@app.route('/api/v1.0/playlist_data/<int:playlist_id>', methods=['GET'])
def get_playlist_data(playlist_id):
    response = read_query_db("SELECT * FROM playlist WHERE id = (%s)",
                             (playlist_id,))
    return response


@app.route('/api/v1.0/user_plays_music_number/<int:user_id>/<int:playlist_id>', methods=['GET'])
def user_plays_playlist_number(user_id, playlist_id):
    response = read_field_query_db(
        "SELECT COUNT(*) FROM user_creates_playlist WHERE user_id = (%s) AND playlist_id = (%s)",
        (user_id, playlist_id))
    return response


@app.route('/api/v1.0/listener_login', methods=['POST'])
def listener_login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    response = read_field_query_db("SELECT password FROM listener WHERE username = (%s)",
                                   (username,))[1:-1]
    if verify_password(response, password):
        return jsonify(status="success",
                       code=200,
                       message="success login")
    else:
        return jsonify(status="failed",
                       code=201,
                       message="login error!")


@app.route('/api/v1.0/listener_signup', methods=['POST'])
def listener_signup():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = hash_password(data.get('password', ''))
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    birth_year = data.get('birth_year', '')
    nationality = data.get('nationality', '')
    q_number = data.get('q_number', '')
    q_value = data.get('q_value', '')
    response = cud_query_db(
        "INSERT INTO listener (username,email,password,first_name,last_name,birth_year,nationality,q_number,q_value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        (username, email, password, first_name, last_name, birth_year, nationality, q_number, q_value))
    return response


@app.route(
    '/api/v1.0/change_user_to_premium/<int:user_id>/days=<int:days>&credit_card=<credit_card>&credit_expiration=<credit_expiration>',
    methods=['GET'])
def change_user_to_premium(user_id, days, credit_card, credit_expiration):
    now = datetime.datetime.utcnow()
    add_to_premium = cud_query_db(
        "INSERT INTO premium (listener_id , days) VALUES (%s,%s)",
        (user_id, days))
    response = cud_query_db(
        "UPDATE listener SET premium_days = (%s),credit_card = (%s),credit_expiration = (%s),buying_date = (%s) "
        "WHERE id = (%s)",
        (days, credit_card, credit_expiration, now.strftime('%Y-%m-%d'), user_id))
    return response


@app.route('/api/v1.0/artist_signup', methods=['POST'])
def artist_signup():
    data = request.get_json()
    username = data.get('username', '')
    email = data.get('email', '')
    password = hash_password(data.get('password', ''))
    artistic_name = data.get('artistic_name', '')
    start_date = data.get('start_date', '')
    nationality = data.get('nationality', '')
    q_number = data.get('q_number', '')
    q_value = data.get('q_value', '')
    response = cud_query_db(
        "INSERT INTO artist (username,email,password,artistic_name,start_date,nationality,q_number,q_value) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
        (username, email, password, artistic_name, start_date, nationality, q_number, q_value))
    artist_id = read_field_query_db("SELECT artist_id FROM artist WHERE username = (%s) AND email = (%s)",
                                    (username, email))
    add_to_waited_artist = cud_query_db(
        "INSERT INTO waiting_artist (waitingartist_id) VALUES (%s)",
        (artist_id,))
    return add_to_waited_artist


def hash_password(password):
    return bcrypt.generate_password_hash(password)


def verify_password(stored_password, provided_password):
    return bcrypt.check_password_hash(stored_password, provided_password)


@app.route('/api/v1.0/user_remember_password', methods=['POST'])
def user_remember_password():
    data = request.form
    username = data.get('username')
    return username


@app.route('/api/v1.0/user_update_account', methods=['POST'])
def user_update_account():
    data = request.form
    username = data.get('username')
    return username


@app.route('/api/v1.0/user_delete_account', methods=['POST'])
def user_delete_account():
    data = request.form
    username = data.get('username')
    return username


def read_field_query_db(query, args=()):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, args)
        rv = cur.fetchone()
        mysql.connection.commit()
        cur.close()
        if cur.rowcount <= 0:
            return jsonify(status="failed",
                           code=201,
                           message="No data found!")
        else:
            return str(rv)[1:str(rv).index(',')]
    except Exception as e:
        cur.close()
        return jsonify(status="failed",
                       code=201,
                       message=str(e))


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
