from flask import Flask
from flask import render_template
from flask import jsonify
from flask_mysqldb import MySQL
from flask import request
import datetime
from flask_bcrypt import Bcrypt
import json
from flask_mail import Mail
from flask_mail import Message

app = Flask(__name__)
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": "greefy.com@gmail.com",
    "MAIL_PASSWORD": "$greefy$__co"
}
app.config.update(mail_settings)
mail = Mail(app)

app.config['JSON_SORT_KEYS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'greefy'
mysql = MySQL(app)
bcrypt = Bcrypt()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login.html')
def login():
    return render_template('login.html')


# ------------------------------Music------------------------------ #
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


@app.route('/api/v1.0/user_plays_music_number/<int:user_id>/<int:music_id>', methods=['GET'])
def user_plays_music_number(user_id, music_id):
    response = read_field_query_db(
        "SELECT COUNT(*) FROM user_plays_music WHERE user_id = (%s) AND music_id = (%s) AND music_date_played BETWEEN CURDATE() - INTERVAL 1 DAY AND CURDATE()",
        (user_id, music_id))
    return response


@app.route('/api/v1.0/music_data/<int:music_id>', methods=['GET'])
def get_music_data(music_id):
    response = read_query_db("SELECT * FROM msuic WHERE id = (%s)",
                             (music_id,))
    return response


@app.route('/api/v1.0/all_music', methods=['GET'])
def get_all_musics():
    response = read_query_db("SELECT * FROM msuic")
    return response


# ------------------------------End Music------------------------------ #


# ------------------------------PlayList------------------------------ #
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


@app.route('/api/v1.0/get_user_playlists/<int:user_id>', methods=['GET'])
def get_user_playlists(user_id):
    response = read_query_db("SELECT * FROM user_shares_playlist WHERE user_id = (%s)",
                             (user_id,))
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


@app.route('/api/v1.0/get_playlist_musics/<int:playlist_id>', methods=['GET'])
def get_playlist_musics(playlist_id):
    response = read_query_db(
        "SELECT music_id , music_added_date FROM playlist_has_music WHERE  playlist_id = (%s) ",
        (playlist_id,))
    return response


@app.route('/api/v1.0/get_playlist_popular_genre/<int:playlist_id>', methods=['GET'])
def get_playlist_popular_genre(playlist_id):
    response = read_query_db(
        "SELECT count(genre) FROM playlist as p INNER JOIN playlist_has_music as ps ON p.id = ps.playlist_id INNER JOIN music as m ON ps.music_id = m.id INNER JOIN album as a ON m.album_id = a.id WHERE p.id = (%s) GROUP BY genre",
        (playlist_id,))
    return response


# ------------------------------EndPlaylist------------------------------ #

# ------------------------------Search------------------------------ #
@app.route('/api/v1.0/search/<search_text>', methods=['GET'])
def search(search_text):
    response = search_query_db(search_text)
    return response


# ------------------------------EndSearch------------------------------ #


# ------------------------------User------------------------------ #
@app.route('/api/v1.0/user_follows/<int:first_user_id>/<int:second_user_id>', methods=['GET'])
def user_follows(first_user_id, second_user_id):
    response = cud_query_db("INSERT INTO user_follows (firstuser_id,seconduser_id) VALUES (%s,%s)",
                            (first_user_id, second_user_id))
    return response


@app.route('/api/v1.0/user_follows_artist/<int:user_id>/<int:artist_id>', methods=['GET'])
def user_follows_artist(user_id, artist_id):
    response = cud_query_db("INSERT INTO user_follows_artist (user_id,artist_id) VALUES (%s,%s)",
                            (user_id, artist_id))
    return response


@app.route('/api/v1.0/user_unfollows/<int:first_user_id>/<int:second_user_id>', methods=['GET'])
def user_unfollows(first_user_id, second_user_id):
    response = cud_query_db("DELETE FROM user_follows WHERE firstuser_id = %s AND seconduser_id = %s",
                            (first_user_id, second_user_id))
    return response


@app.route('/api/v1.0/user_unfollows_artist/<int:user_id>/<int:artist_id>', methods=['GET'])
def user_unfollows_artist(user_id, artist_id):
    response = cud_query_db("DELETE FROM user_follows_artist WHERE user_id = %s AND artist_id = %s",
                            (user_id, artist_id))
    return response


@app.route('/api/v1.0/get_user_data/username=<username>&email=<email>/', methods=['GET'])
def get_user_data(username, email):
    response = read_query_db("SELECT * FROM listener WHERE username = (%s) AND email = (%s)",
                             (username, email))
    return response


@app.route('/api/v1.0/get_user_profile/username=<username>&email=<email>,<user_type>/', methods=['GET'])
def get_user_profile(username, email, user_type):
    if user_type == 'artist':
        pass

    elif user_type == 'listener':
        pass
    else:
        response = """{
                    status:"failed"
                    code=201
                    error:'type is invalid!'
                   }
                    """
    return response


@app.route('/api/v1.0/get_user_followers/<int:user_id>', methods=['GET'])
def get_user_followers(user_id):
    response = read_query_db("SELECT firstuser_id FROM user_follows WHERE seconduser_id = (%s)",
                             (user_id,))
    return response


@app.route('/api/v1.0/get_user_followings/<int:user_id>', methods=['GET'])
def get_user_followings(user_id):
    response = read_query_db("SELECT seconduser_id FROM user_follows WHERE firstuser_id = (%s)",
                             (user_id,))
    return response


@app.route('/api/v1.0/get_last_music_followers_play/<int:user_id>', methods=['GET'])
def get_last_music_followers_play(user_id):
    response = read_query_db("SELECT firstuser_id FROM user_follows WHERE seconduser_id = (%s)",
                             (user_id,))
    result = json.loads(response.get_data().decode("utf-8"))['content']
    temp = list()
    final_list = list()
    for x in result:
        temp.append(x['firstuser_id'])
    for i in range(len(temp)):
        find_music = read_query_db(
            "SELECT music_id FROM user_plays_music WHERE user_id = (%s) AND music_date_played IN (SELECT max(music_date_played) FROM user_plays_music) ORDER BY music_time_played desc limit 1 offset 1"
            , (temp.__getitem__(i),))
        final_result = json.loads(find_music.get_data().decode("utf-8"))
        if final_result['code'] == 200:
            final_list.append(final_result['content'])
    return str(final_list)


@app.route('/api/v1.0/get_five_music_from_artist/<int:user_id>', methods=['GET'])
def get_five_music_from_artist(user_id):
    response = read_query_db(
        "SELECT music.id FROM music INNER JOIN album ON music.album_id = album.id INNER JOIN user_follows_artist on album.artist_id = user_follows_artist.artist_id WHERE user_follows_artist.user_id = (%s) LIMIT 5",
        (user_id,))
    return response


@app.route('/api/v1.0/get_five_music_week_popular', methods=['GET'])
def get_five_music_week_popular():
    response = read_query_db(
        "select u.music_id from user_plays_music as u inner join user_likes_music as ul on u.music_id = ul.music_id group by u.music_id order by count(u.music_id) limit 5")
    return response


@app.route('/api/v1.0/get_user_popular_genre/<int:user_id>', methods=['GET'])
def get_user_popular_genre(user_id):
    response = read_query_db(
        "SELECT count(genre) FROM listener as l INNER JOIN user_plays_music as u ON l.id = u.user_id INNER JOIN music as m ON m.id = u.music_id INNER JOIN album as a ON a.id = m.album_id WHERE l.id = (%s) GROUP BY genre"
        , (user_id,))
    return response


@app.route('/api/v1.0/get_artist_music_number_in_genre/<int:artist_id>', methods=['GET'])
def get_artist_music_number_in_genre(artist_id):
    response = read_query_db(
        "SELECT count(genre) FROM artist as a INNER JOIN album as al ON a.artist_id = al.artist_id INNER JOIN music as m ON m.album_id = al.id WHERE a.artist_id = (%s) GROUP BY genre"
        , (artist_id,))
    return response


@app.route('/api/v1.0/suggest_music_to_user/playlist_id=<int:playlist_id>&genre=<genre>', methods=['GET'])
def suggest_music_to_user(playlist_id, genre):
    response = read_query_db(
        "SELECT m.id FROM music as m INNER JOIN album as a ON m.album_id = a.id WHERE a.genre = (%s) AND NOT EXISTS (SELECT * FROM playlist_has_music as p WHERE p.playlist_id = (%s) AND p.music_id = m.id) ORDER BY RAND() LIMIT 2",
        (genre, playlist_id,))
    return response


@app.route('/api/v1.0/suggest_album_to_user/<nationality>', methods=['GET'])
def suggest_album_to_user(nationality):
    response = read_query_db(
        "SELECT a.id FROM album as a INNER JOIN artist as ar ON a.artist_id = ar.artist_id WHERE ar.nationality = (%s)",
        (nationality,))
    return response


@app.route('/api/v1.0/show_artist_to_admin', methods=['GET'])
def show_artist_to_admin():
    response = read_query_db(
        "SELECT a.artist_id FROM artist as a INNER JOIN album as al ON al.artist_id = a.artist_id GROUP BY a.artist_id ORDER BY count(a.artist_id)")
    return response


@app.route('/api/v1.0/find_artist_fans/artist_id=<int:artist_id>&artist_genre=<artist_genre>&user_genre=<user_genre>',
           methods=['GET'])
def find_artist_fans(artist_id, artist_genre, user_genre):
    if check_genre(artist_genre, user_genre):
        response = read_query_db(
            "SELECT l.id FROM listener as l INNER JOIN user_plays_music as u ON l.id = u.user_id INNER JOIN music as m ON u.music_id = m.id INNER JOIN album as a ON a.id = m .album_id WHERE count(l.id) > 9 AND a.artist_id = (%s)",
            (artist_id,))
        return response
    else:
        return failed_genres(artist_genre, user_genre)


def check_genre(artist_genre, user_genre):
    if artist_genre == user_genre:
        return True
    else:
        return False


def failed_genres(artist_genre, user_genre):
    if artist_genre != user_genre:
        return jsonify(status="failed",
                       code=201,
                       message="artist_genre is not equal to user_genre")


@app.route('/api/v1.0/send_email', methods=['POST'])
def send_email():
    try:
        data = request.get_json()
        subject = data.get('subject', '')
        recipient_email = data.get('recipient_email', '')
        recipient_username = data.get('recipient_username', '')
        body = data.get('body', '')
        response = cud_query_db(
            "INSERT INTO mail (subject,recipient_email,recipient_username,body) VALUES (%s,%s,%s,%s)",
            (subject, recipient_email, recipient_username, body,))
        msg = mail.send_message(
            subject,
            sender='greefy.co@gmail.com',
            recipients=[recipient_email],
            body=body
        )
        mail.send(msg)
        return jsonify(status="success",
                       code=200,
                       message="done!",
                       )
    except Exception as e:
        return jsonify(status="failed",
                       code=201,
                       message=str(e))


# ------------------------------EndUser------------------------------ #


# ------------------------------Album------------------------------ #
@app.route('/api/v1.0/user_delete_music_from_album/<int:album_id>/<int:music_id>', methods=['GET'])
def user_delete_music_from_album(album_id, music_id):
    response = cud_query_db(
        "DELETE FROM music WHERE  album_id = (%s) AND music_id = (%s)",
        (album_id, music_id,))
    return response


@app.route('/api/v1.0/user_delete_music_from_album/<int:album_id>', methods=['GET'])
def user_delete_album(album_id):
    response = cud_query_db(
        "DELETE FROM album WHERE  album_id = (%s)",
        (album_id,))
    return response


@app.route('/api/v1.0/get_album_musics/<int:album_id>', methods=['GET'])
def get_album_musics(album_id):
    response = read_query_db(
        "SELECT title, duration FROM music WHERE  album_id = (%s) ",
        (album_id,))
    return response


# ------------------------------EndAlbum------------------------------ #


# ------------------------------Admin------------------------------ #
@app.route('/api/v1.0/user_report_music_to_admin/<int:music_id>', methods=['GET'])
def user_report_music_to_admin(music_id):
    response = cud_query_db(
        "INSERT INTO reported_music (reportedmusic_id) VALUES (%s)",
        (music_id,))
    return response


# ------------------------------EndAdmin------------------------------ #


# ------------------------------Login&Signup------------------------------ #
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


@app.route('/api/v1.0/listener_remember_password/username=<username>&q_value=<q_value>', methods=['GET'])
def listener_remember_password(username,q_value):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM listener WHERE username = (%s) AND q_value = (%s) ",
        (username,q_value,))
    mysql.connection.commit()
    if cur.rowcount <= 0:
        listener_message = jsonify(status="failed",
                                   code=201,
                                   message="No data found!")
    else:
        listener_message = jsonify(status="success",
                                   code=200,
                                   message="done!")
    return listener_message


@app.route('/api/v1.0/artist_remember_password/username=<username>&q_value=<q_value>', methods=['GET'])
def artist_remember_password(username,q_value):
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT * FROM artist WHERE username = (%s) AND q_value = (%s) ",
        (username,q_value,))
    mysql.connection.commit()
    if cur.rowcount <= 0:
        artist_message = jsonify(status="failed",
                                   code=201,
                                   message="No data found!")
    else:
        artist_message = jsonify(status="success",
                                   code=200,
                                   message="done!")
    return artist_message


@app.route('/api/v1.0/listener_update_account/<int:user_id>', methods=['POST'])
def listener_update_account(user_id):
    data = request.get_json()
    email = data.get('email', '')
    password = hash_password(data.get('password', ''))
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')
    birth_year = data.get('birth_year', '')
    nationality = data.get('nationality', '')
    response = cud_query_db(
        "UPDATE listener SET email = (%s),password = (%s),first_name = (%s),last_name = (%s),birth_year (%s),nationality = (%s) WHERE id = (%s)",
        (email, password, first_name, last_name, birth_year, nationality, user_id))
    return response


@app.route('/api/v1.0/artist_update_account/<int:user_id>', methods=['POST'])
def artist_update_account(user_id):
    data = request.get_json()
    email = data.get('email', '')
    password = hash_password(data.get('password', ''))
    artistic_name = data.get('artistic_name', '')
    nationality = data.get('nationality', '')
    response = cud_query_db(
        "UPDATE artist SET email = (%s),password = (%s),artistic_name = (%s),nationality = (%s) WHERE id = (%s)",
        (email, password, artistic_name, nationality, user_id))
    return response


@app.route('/api/v1.0/listener_delete_account/<int:user_id>', methods=['GET'])
def listener_delete_account(user_id):
    response = cud_query_db("DELETE FROM listener WHERE id = (%s)",
                            (user_id,))
    return response


@app.route('/api/v1.0/artist_delete_account/<int:user_id>', methods=['GET'])
def artist_delete_account(user_id):
    response = cud_query_db("DELETE FROM artist WHERE artist_id = (%s)",
                            (user_id,))
    return response


# ------------------------------EndLogin&Signup------------------------------ #


# ------------------------------Premium------------------------------ #
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


@app.route(
    '/api/v1.0/change_user_to_free/<int:user_id>',
    methods=['GET'])
def change_user_to_free(user_id):
    delete_from_premium = cud_query_db(
        "DELETE FROM premium WHERE listener_id = (%s)",
        (user_id,))
    response = cud_query_db(
        "UPDATE listener SET premium_days = (%s),credit_card = (%s),credit_expiration = (%s),buying_date = (%s) "
        "WHERE id = (%s)",
        (0, "", "", "", user_id))
    return response


# ------------------------------EndPremium------------------------------ #


# ------------------------------Config------------------------------ #
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


def search_query_db(search_text):
    try:
        cur = mysql.connection.cursor()
        # listener query
        cur.execute(
            """SELECT * FROM listener WHERE username 
            LIKE CONCAT('%%',%s,'%%') OR 
            first_name LIKE CONCAT('%%',%s,'%%') OR 
            last_name LIKE CONCAT('%%',%s,'%%')""",
            (search_text, search_text, search_text,))
        listener_result = cur.fetchall()
        mysql.connection.commit()
        if cur.rowcount <= 0:
            listener_message = "No data found!"
        else:
            listener_message = [{cur.description[index][0]: column for index, column in enumerate(value)} for value in
                                listener_result]
        # artist query
        cur.execute(
            """SELECT * FROM artist WHERE username
            LIKE CONCAT('%%',%s,'%%') OR
            artistic_name LIKE CONCAT('%%',%s,'%%')""",
            (search_text, search_text,))
        artist_result = cur.fetchall()
        mysql.connection.commit()
        if cur.rowcount <= 0:
            artist_message = "No data found!"
        else:
            artist_message = [{cur.description[index][0]: column for index, column in enumerate(value)} for value in
                              artist_result]
        # music query
        cur.execute("SELECT * FROM music WHERE title LIKE CONCAT('%%',%s,'%%')",
                    (search_text,))
        music_result = cur.fetchall()
        mysql.connection.commit()
        if cur.rowcount <= 0:
            music_message = "No data found!"
        else:
            music_message = [{cur.description[index][0]: column for index, column in enumerate(value)} for value in
                             music_result]
        # album query
        cur.execute("SELECT * FROM album WHERE title LIKE CONCAT('%%',%s,'%%')",
                    (search_text,))
        album_result = cur.fetchall()
        mysql.connection.commit()
        if cur.rowcount <= 0:
            album_message = "No data found!"
        else:
            album_message = [{cur.description[index][0]: column for index, column in enumerate(value)} for value in
                             album_result]
        # playlist query
        cur.execute("SELECT * FROM playlist WHERE title LIKE CONCAT('%%',%s,'%%')",
                    (search_text,))
        playlist_result = cur.fetchall()
        mysql.connection.commit()
        if cur.rowcount <= 0:
            playlist_message = "No data found!"
        else:
            playlist_message = [{cur.description[index][0]: column for index, column in enumerate(value)} for value in
                                playlist_result]
        cur.close()
        return jsonify(status="success",
                       code=200,
                       message="done!",
                       listener=listener_message,
                       artist=artist_message,
                       music=music_message,
                       album=album_message,
                       playlist=playlist_message, )
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


# ------------------------------EndConfig------------------------------ #


if __name__ == '__main__':
    app.run()
