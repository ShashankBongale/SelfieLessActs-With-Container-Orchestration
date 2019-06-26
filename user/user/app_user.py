from flask import Flask, jsonify, request, abort
import re
import pickle

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
    usernames = [user['username'] for user in user_list]	#List of existing usernames in the database
    if(request.json["username"] not in usernames):
        hex_characters = ['a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9']
        password = request.json["password"]
        if(len(password) == 40):
            for i in password:
                if(i not in hex_characters):
                    abort(400)
            user = dict()
            user["username"] = request.json["username"]
            user["password"] = request.json["password"]
            user_list.append(user)
            return jsonify({}),201
        else:
            abort(400)
    else:
        abort(405)

# 2_final [Remove users]
@app.route('/api/v1/users/<string:username>',methods = ['DELETE'])
def rem_user(username):
    global app_count
    app_count = app_count + 1
    #print(username)
    users = []
    for i in user_list:
        users.append(i["username"])
    if(username in users):
        index = users.index(username)
        del(user_list[index])
        return jsonify({}),200
    else:
        abort(405)

# 3 list all users
@app.route('/api/v1/users', methods = ['GET'])
def list_users():
    global app_count
    app_count = app_count + 1
    if(len(user_list) > 0):
        usernames = [user['username'] for user in user_list]
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

