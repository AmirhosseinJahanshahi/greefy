from flask import Flask
from flask import jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'spotify'
mysql = MySQL(app)


@app.route('/api/v1.0/', methods=['GET'])
def hello_world():
    response = read_query_db("SELECT * FROM admin")
    return response


def read_query_db(query, args=()):
    try:
        cur = mysql.connection.cursor()
        cur.execute(query, args)
        rv = cur.fetchall()
        mysql.connection.commit()
        cur.close()
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
                       message="edited!")
    except Exception as e:
        cur.close()
        return jsonify(status="failed",
                       code=201,
                       message=str(e))



if __name__ == '__main__':
    app.run()
