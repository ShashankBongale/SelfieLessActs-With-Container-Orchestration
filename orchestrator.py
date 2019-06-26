from flask import Flask, jsonify, request, abort, redirect, url_for , Response
import requests
import os
import re
import pickle
from threading import Thread, Lock
import sys
import time
import json

container_dictionary = {}
number_of_requests = 0
first_request = False
lock_number_of_requests = Lock()
container_dictionary_lock = Lock()
app = Flask(__name__)
current_container = 0

first_container_ip = 8000
scaling_check_interval = 120
scaling_container_bracket = 20
fault_tolerance_check_interval = 1

def start_last_container():
    max_cont_id = max(list(container_dictionary.keys()))
    container_id = os.popen("sudo docker run -v saksham:/app_act -p " + str(max_cont_id + 1) + ":80 -d acts").read().rstrip()
    container_dictionary[max_cont_id + 1] = container_id

def kill_last_container():
    max_cont_id = max(list(container_dictionary.keys()))
    cont_id_kill = container_dictionary[max_cont_id]
    tmp = os.popen("sudo docker container kill " + cont_id_kill).read()
    del(container_dictionary[max_cont_id])


def auto_scale():
    global number_of_requests
    print('Auto Scaling Started', file=sys.stderr)
    while(1):
        time.sleep(scaling_check_interval)
        lock_number_of_requests.acquire()
        container_dictionary_lock.acquire()
        num_cont_needed = (number_of_requests // scaling_container_bracket) + 1
        if(len(container_dictionary) != num_cont_needed):
            if(len(container_dictionary) < num_cont_needed):
                no_of_extra_containers = num_cont_needed - len(container_dictionary)
                for i in range(no_of_extra_containers):
                    start_last_container()
                    time.sleep(1)
                print(container_dictionary,file=sys.stderr)
            else:
                no_of_extra_containers = abs(num_cont_needed - len(container_dictionary))
                while(no_of_extra_containers != 0):
                    kill_last_container()
                    no_of_extra_containers = no_of_extra_containers - 1
                print(container_dictionary,file=sys.stderr)
        else:
            print("Same number of containers",file=sys.stderr)
        number_of_requests = 0
        container_dictionary_lock.release()
        lock_number_of_requests.release()

def load_balancer_handler(url):
    lock_number_of_requests.acquire()
    global number_of_requests, first_request
    if(first_request == False):
      first_request = True
      # number_of_requests += 1
      t1 = Thread(target=auto_scale)
      t1.start()
    if("localhost" in url):
      parts = url.split("http://localhost")
      #lb1-2139422882.us-east-1.elb.amazonaws.com
    elif("35.171.62.224" in url):
      parts = url.split("http://35.171.62.224")
    else:
      parts = url.split("http://lb1-2139422882.us-east-1.elb.amazonaws.com")
    global current_container
    container_dictionary_lock.acquire()
    current_container = (current_container + 1) % len(container_dictionary)
    new_url = "http://127.0.0.1:"+str(current_container + first_container_ip)+parts[1]
    container_dictionary_lock.release()
    resp = requests.request(
        method=request.method,
        url= new_url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data())
    headers = [(name, value) for (name, value) in resp.raw.headers.items()]#refer back
    response = Response(resp.content, resp.status_code, headers)
    number_of_requests = number_of_requests + 1 #repeated after
    lock_number_of_requests.release()
    return response

def fault_tolerance():
    print("Fault tolereance started",file=sys.stderr)
    while(1):
        print("Fault check",file=sys.stderr)
        time.sleep(fault_tolerance_check_interval)
        container_dictionary_lock.acquire()

        active_containers = list(container_dictionary.keys())
        for container_ip in active_containers:
            request_ = requests.get("http://127.0.0.1:"+str(container_ip)+"/api/v1/_health")
            if(request_.status_code == 500):
                os.popen("sudo docker container kill " + container_dictionary[container_ip]).read()
                del(container_dictionary[container_ip])
                container_id = os.popen("sudo docker run -v saksham:/app_act -p " + str(container_ip) + ":80 -d acts").read().rstrip()
                container_dictionary[container_ip] = container_id
                print("started a new container for "+str(container_ip),file=sys.stderr)

        container_dictionary_lock.release()


def init_container():
    con = os.popen("sudo docker run -v saksham:/app_act -p  "+str(first_container_ip)+":80 -d acts").read()
    con_real = con.rstrip()
    container_dictionary[first_container_ip] = con_real

@app.route('/api/v1/categories', methods=['GET'])
def fun():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/categories', methods=['POST'])
def cat_post():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/categories/<string:categoryName>', methods=['DELETE'])
def rem_cat(categoryName):
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/categories/<string:categoryName>/acts', methods=['GET'])
def list_acts_for_category(categoryName):
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/categories/<string:categoryName>/acts/size', methods=['GET'])
def number_of_acts_for_category(categoryName):
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/acts/upvote', methods=['POST'])
def upvote_an_act():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/acts/<int:task_id>',methods = ['DELETE'])
def delete_act(task_id):
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/acts', methods=['POST'])
def upload_an_act():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/_count',methods=['GET'])
def count_fun():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/_count',methods=['DELETE'])
def del_count():
    response = load_balancer_handler(request.url)
    return response

@app.route('/api/v1/acts/count',methods=['GET'])
def count1():
    response = load_balancer_handler(request.url)
    return response

def generic_orchestrator_configuration():
    global first_container_ip
    global scaling_check_interval
    global scaling_container_bracket
    global fault_tolerance_check_interval
    if(os.path.isfile("orch_config.txt")):
        with open("orch_config.txt") as json_file:
            configurations = json.load(json_file)
            if("first_container_ip" in configurations.keys()):
                first_container_ip = int(configurations["first_container_ip"])
            if("scaling_check_interval" in configurations.keys()):
                scaling_check_interval = int(configurations["scaling_check_interval"])
            if("scaling_container_bracket" in configurations.keys()):
                scaling_container_bracket = int(configurations["scaling_container_bracket"])
            if("fault_tolerance_check_interval" in configurations.keys()):
                fault_tolerance_check_interval = int(configurations["fault_tolerance_check_interval"])

if __name__ == '__main__':
    generic_orchestrator_configuration()
    print("first_container_ip", first_container_ip)
    print("scaling_check_interval", scaling_check_interval)
    print("scaling_container_bracket", scaling_container_bracket)
    print("fault_tolerance_check_interval", fault_tolerance_check_interval)
    init_container()
    Thread(target = fault_tolerance).start()
    app.run("0.0.0.0",port=80)
