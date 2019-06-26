from flask import Flask, jsonify, request, abort
import re
import pickle
#d
app = Flask(__name__)

# categories = set(["category1", "category2"]);
#
# no_of_acts_categories_dict = {
#     "category1" : 0,
#     "category2" : 0,
# }
#
# user_list = [] #List of dictionaries with each dictionary corresponding to one user with 2 keys : username and password
#
# range_list = []
k=0
#
# acts_list_categories_dict = {
#     "category1" : [],
#     "category2" : [],
# }
@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
  return response

# 1_final [Add users]
@app.route('/api/v1/users',methods = ['POST'])
def add_user():
    if not request.is_json or len(request.json) != 2:
        abort(400)
    users = []	#List of existing usernames in the database
    for i in user_list:
        users.append(i["username"])
    if(request.json["username"] not in users):
        hex = ['a','b','c','d','e','f','0','1','2','3','4','5','6','7','8','9']
        passwd = request.json["password"]
        if(len(passwd) == 40):
            for i in passwd:
                if(i not in hex):
                    abort(400)
            d = {}
            d["username"] = request.json["username"]
            d["password"] = request.json["password"]
            user_list.append(d)
            return jsonify({}),201
        else:
            abort(400)
    else:
        abort(405)

# 2_final [Remove users]
@app.route('/api/v1/users/<string:username>',methods = ['DELETE'])
def rem_user(username):
    #print(username)
    if not request.is_json or len(request.json) != 0:
        abort(400)
    users = []
    for i in user_list:
        users.append(i["username"])
    if(username in users):
        index = users.index(username)
        del(user_list[index])
        return jsonify({}),200
    else:
        abort(405)

# 3_final [List all categories]
@app.route('/api/v1/categories', methods=['GET'])
def list_categories():
    if not request.is_json :
         abort(405)
    if(len(categories) > 0):
        return jsonify(no_of_acts_categories_dict),200
    else:
        return jsonify({}),204


# 4_final  [Add a category]
@app.route('/api/v1/categories', methods=['POST'])
def add_category():
    if not request.is_json or len(request.json) != 1:
        abort(400)
    elif request.json[0] not in categories:
        category = request.json[0]
        no_of_acts_categories_dict[category] = 0
        acts_list_categories_dict[category] = []
        categories.add(category)
    else:
        abort(405)
    return jsonify({}), 201

# 5_final  [Remove a category]
@app.route('/api/v1/categories/<string:categoryName>', methods=['DELETE'])
def remove_category(categoryName):
    if not request.is_json or len(request.json) != 0:
        abort(400)
    elif categoryName in no_of_acts_categories_dict.keys() and categoryName in categories:
        no_of_acts_categories_dict.pop(categoryName)
        acts_list_categories_dict.pop(categoryName)
        categories.remove(categoryName)
        return jsonify({}), 200
    else:
        abort(405)

# 6_final  [List acts for a given category]
@app.route('/api/v1/categories/<string:categoryName>/acts', methods=['GET'])
def list_acts_for_category(categoryName):
    if not request.is_json:
        abort(400)
    if 'start' in request.args and 'end' in request.args:
        startRange = int(request.args.get('start'))
        endRange = int(request.args.get('end'))
        if categoryName not in no_of_acts_categories_dict.keys():
            return jsonify([]), 405
        elif (startRange<1) or (endRange>no_of_acts_categories_dict[categoryName]):
            abort(400)
        elif (endRange-startRange+1>100):
            abort(413)
        else:
            ans = []
            i = len(acts_list_categories_dict[categoryName])-startRange
            f = endRange-startRange+1
            while(f>0):
                ans.append(acts_list_categories_dict[categoryName][i])
                i = i-1
                f = f-1
            return jsonify(ans), 200
    if categoryName in acts_list_categories_dict:
        acts_list = acts_list_categories_dict[categoryName]
        len_acts_list = len(acts_list)
        if(len_acts_list == 0):
            return jsonify([]), 204
        elif(len_acts_list > 100) :
            abort(413)
        else:
            return jsonify(acts_list), 200
    else:
        abort(405)


# 7_final [Number of acts in a category]
@app.route('/api/v1/categories/<string:categoryName>/acts/size', methods=['GET'])
def number_of_acts_for_category(categoryName):
    if not request.is_json or len(request.json) != 0:
        abort(400)
    elif categoryName not in no_of_acts_categories_dict.keys():
        return jsonify([]), 405
    elif categoryName in no_of_acts_categories_dict.keys():
        return jsonify([no_of_acts_categories_dict[categoryName]])
    else:
        abort(405)

# 9_final [Upvote an act]
@app.route('/api/v1/acts/upvote', methods=['POST'])
def upvote_an_act():
	if not request.is_json or len(request.json) != 1:
	        abort(400)
	for i in acts_list_categories_dict.values():
		for j in i:
			if j["actId"]==request.json[0]:
				j["upvotes"] = j["upvotes"]+1
				return jsonify({}), 200
	abort(405)
# 10_final [Remove an act]
@app.route('/api/v1/acts/<int:task_id>',methods = ['DELETE'])
def delete_act(task_id):
    if not request.is_json or len(request.json) != 0:
            abort(400)
    # for i in acts_list_categories_dict.values():
    #     for j in range(len(i)):
    #         if j["actId"]==task_id:
    #             del(j)
    #             return jsonify({}), 200
    category_list = list(acts_list_categories_dict.keys())
    for i in (category_list):
        act_list = acts_list_categories_dict[i]
        flag = 0
        for j in range(len(act_list)):
            if(act_list[j]["actId"] == task_id):
                del(act_list[j])
                no_of_acts_categories_dict[i] = no_of_acts_categories_dict[i] - 1
                return jsonify({}),200
    abort(405)

@app.route('/api/v1/acts', methods=['POST'])
def upload_an_act():
    if not request.is_json or len(request.json) != 6:
        abort(400)
    #The ​actID​ in the request body must be globally unique(1,7)
    for i in acts_list_categories_dict.values():
        for j in i:
            if j["actId"]==request.json["actId"]:
                abort(405)

    #Validatin date and time (2)
    if(not re.match('[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9][0-9][0-9]:[0-9][0-9]\-[0-9][0-9]\-[0-9][0-9]', request.json["timestamp"])):
        abort(400)
    flag = 0
    for i in user_list:
        if i["username"] == request.json["username"]:
            flag = 1
            break
    if flag==0:
        abort(405)


    #No upvotes field should be sent(5)
    if "upvotes" in request.json.keys():
        abort(400)

    #The category name must exist(6)
    if request.json["categoryName"] not in categories:
        abort(405)

    # Validating base_64 password
    # if( not re.match(r"^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$", json.request["imgB64"])):
    #      abort(400)
    def is_base64(string):
        if len(string) % 4 == 0 and re.match('^[A-Za-z0-9+\/=]+\Z', string):
            return(True)
        else:
            return(False)

    # if (not is_base64(request.json["imgB64"])):
    #     abort(400)

    #Uploading the act
    no_of_acts_categories_dict[request.json["categoryName"]] = no_of_acts_categories_dict[request.json["categoryName"]]+1
    d = dict()
    d["actId"] = request.json["actId"]
    d["timestamp"] = request.json["timestamp"]
    d["caption"] = request.json["caption"]
    d["upvotes"] = 0
    d["imgB64"] = request.json["imgB64"]
    d["username"] = request.json["username"]
    acts_list_categories_dict[request.json["categoryName"]].append(d)
    return jsonify({}), 201

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    pickle.dump(categories, open("categories.p", "wb"))
    pickle.dump(no_of_acts_categories_dict, open("no_of_acts_categories_dict.p", "wb"))
    pickle.dump(user_list, open("user_list.p", "wb"))
    pickle.dump(range_list, open("range_list.p", "wb"))
    pickle.dump(acts_list_categories_dict, open("acts_list_categories_dict.p", "wb"))
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'

if __name__ == '__main__':
    no_of_acts_categories_dict = pickle.load(open("no_of_acts_categories_dict.p", "rb"))
    categories = pickle.load(open("categories.p", "rb"))
    user_list = pickle.load(open("user_list.p", "rb"))
    range_list = pickle.load( open("range_list.p", "rb"))
    acts_list_categories_dict = pickle.load(open("acts_list_categories_dict.p", "rb"))
    app.run(debug=True)
