from flask import Flask, jsonify, request, abort
import re
import pickle
import sqlite3
import sys
app = Flask(__name__)
app_count = 0
# user_list = [] #List of dictionaries with each dictionary corresponding to one user with 2 keys : username and password

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

# 1_final [Add users]
@app.route('/api/v1/users',methods = ['POST'])
def add_user():
    global app_count
    app_count = app_count + 1
    connection = sqlite3.connect('user.db')
    res = list(connection.execute("SELECT user_name,password FROM users"))
    usernames = [i[0] for i in res]
    if(request.json["username"] not in usernames):
        hex_characters = ['a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9']
        password = request.json["password"]
        if(len(password) == 40):
            for i in password:
                if(i not in hex_characters):
                    connection.close()
                    abort(400)
            name = request.json["username"]
            command = "INSERT INTO users values "+"('" + name + "','" + password + "')"
            connection.execute(command)
            connection.commit()
            connection.close()
            return jsonify({}),201
        else:
            connection.close()
            abort(400)
    else:
        connection.close()
        abort(405)
# 2_final [Remove users]
@app.route('/api/v1/users/<string:username>',methods = ['DELETE'])
def rem_user(username):
    global app_count
    app_count = app_count + 1
    connection = sqlite3.connect('user.db')
    res = list(connection.execute("SELECT user_name,password FROM users"))
    users_list = [i[0] for i in res]
    print(users_list,file=sys.stderr)
    if(username in users_list):
        command = "DELETE from users where user_name = " + "'"+ username + "'"
        connection.execute(command)
        connection.commit()
        connection.close()
        return jsonify({}),200
    else:
        connection.close()
        abort(405)
# 3 list all users
@app.route('/api/v1/users', methods = ['GET'])
def list_users():
    global app_count
    app_count = app_count + 1
    connection = sqlite3.connect('user.db')
    res = list(connection.execute("SELECT user_name,password FROM users"))
    connection.close()
    if(len(res) > 0):
        usernames = [i[0] for i in res]
        return jsonify(usernames),200
    else:
        return jsonify({}),204
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    pickle.dump(user_list, open("user_list.p", "wb"))
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

@app.route('/api/v1/_count',methods=['GET'])
def count_fun():
    count_list = []
    count_list.append(app_count)
    return jsonify(count_list),200
@app.route('/api/v1/_count',methods=['DELETE'])
def del_count():
    global app_count
    app_count = 0
    return jsonify({}),200

if __name__ == '__main__':
    user_list = pickle.load(open("user_list.p", "rb"))
    app.run("0.0.0.0",port=80)
