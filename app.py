# TODO:
# 1. Main page - get user input zipcode

# 2. Result page - get places from google API

# 3. Login page
# 4. Reviews page
import re
import time
from flask import Flask, json, render_template, jsonify, request, redirect, url_for
from numpy import rad2deg
from pymongo.message import _raise_document_too_large
import add_data as ad
app = Flask(__name__, template_folder='./templates')

import requests
from pymongo import MongoClient

client = MongoClient('localhost',27017)
db = client.polar

@app.route('/')
def home():
   return render_template('home.html')

@app.route('/signin')
def moveto_signin():
    return render_template('signin.html')

@app.route('/signup')
def moveto_signup():
    return render_template('signup.html')

@app.route('/test_hospital')
def test_hospital():
    print(1)
    return render_template('hospital.html')
# ----------------------------------------------------------------------#
# 주석처리 된 것은 user_input 이 place name 인 경우와 zipcode 인 경우를 고려한 것.
# current status: zipcode만 고려하는 상황
# ----------------------------------------------------------------------#
@app.route('/search/hospital', methods=['POST'])
def hospital_searching():
    user_input = str(request.form['user_input'])
    range_selection = float(request.form['range_selection'])
    loc = db.ziplatlong.find_one({'zipcode':user_input},{'_id':0})
        # insert zipcode in ziplatlong, find hospitals from API, insert int db.hospital
        # return query result
    if loc is None:
        l = ad.insert_zipcode_loc(user_input)
        ad.insert_hospital(l, range_selection)
    else:
        ad.insert_hospital(loc, range_selection)
    result = list(db.hospital.find({'zipcode': user_input}, {'_id': 0}))
    return jsonify({'result': 'success', 'hospitals' : result})
    # res = re.match("[-+]?\d+$", user_input)
    # if res: # user_input = zipcode
    #     if loc is None:
    #         # insert zipcode in ziplatlong, find hospitals from API, insert int db.hospital
    #         # return query result
    #         l = ad.insert_zipcode_loc(user_input)
    #         ad.insert_hospital(l, range_selection)
    # else: # user_input = name of the place
    #     if user_input in db:
    #         return 0
    #         # query from db.hospital by name
    #         # & get postal code
    #         # & get nearby postal code and get from db or api
    #     else:
    #         # ad.insert_hospital(user_input)
    #         return 0

# TODO: passing over variables
@app.route('/search/hospital', methods=['GET'])
def hospital_trigger():
    service_selection = request.args.get('service')
    user_input = request.args.get('input')
    range_selection = request.args.get('radius')
    # return redirect(url_for("hospital_result", s=service_selection, u=user_input, r=range_selection))
    # return redirect(url_for("test_hospital"))
    res = url_for("hospital_result", service=service_selection, input=user_input, radius=range_selection)
    return jsonify({
        'route': res
    })
    # loc = db.ziplatlong.find_one({'zipcode':user_input},{'_id':0})
    # result = list(db.hospital.find({'zipcode': user_input}, {'_id': 0}))
    # return render_template('hospital.html', service=service_selection, input=user_input, radius=range_selection)
    # return jsonify({'result': 'success', 'hospitals': result})
@app.route('/search', methods=['GET'])
def hospital_result():
    print("rendering")
    # service_selection = request.args.get('s')
    # user_input = request.args.get('u')
    # range_selection = request.args.get('r')
    return render_template('hospital.html')
# ----------------------------------------------------------------------#
# Shelter search
# ----------------------------------------------------------------------#
@app.route('/search/shelter', methods=['POST'])
def shelter_searching():
    user_input = str(request.form['user_input'])
    range_selection = float(request.form['range_selection'])
    loc = db.ziplatlong.find_one({'zipcode':user_input},{'_id':0})
        # insert zipcode in ziplatlong, find hospitals from API, insert int db.hospital
        # return query result
    if loc is None:
        l = ad.insert_zipcode_loc(user_input)
        ad.insert_shelter(l, range_selection)
    else:
        ad.insert_shelter(loc, range_selection)
    result = list(db.shelter.find({'zipcode': user_input}, {'_id': 0}))
    return jsonify({'result': 'success', 'shelters' : result})

@app.route('/search/shelter', methods=['GET'])
def shelter_trigger():
    service_selection = request.args.get('service')
    user_input = request.args.get('input')
    range_selection = request.args.get('radius')
    # return redirect(url_for("hospital_result", s=service_selection, u=user_input, r=range_selection))
    # return redirect(url_for("test_hospital"))
    res = url_for("shelter_result", service=service_selection, input=user_input, radius=range_selection)
    return jsonify({
        'route': res
    })
    # loc = db.ziplatlong.find_one({'zipcode':user_input},{'_id':0})
    # result = list(db.hospital.find({'zipcode': user_input}, {'_id': 0}))
    # return render_template('hospital.html', service=service_selection, input=user_input, radius=range_selection)
    # return jsonify({'result': 'success', 'hospitals': result})
@app.route('/search', methods=['GET'])
def shelter_result():
    print("rendering")
    # service_selection = request.args.get('s')
    # user_input = request.args.get('u')
    # range_selection = request.args.get('r')
    return render_template('shelter.html')

@app.route('/search/hospital/result', methods=['GET'])
def get_near_hospitals():
    user_input = request.args.get('user_input')
    range_selection = request.args.get('radius')
    res = ad.get_near_hospital(user_input, range_selection)
    return jsonify({'result': res})

@app.route('/search/hospital/result/details', methods=['GET'])
def get_hospital_details():
    print(1)
    gplace_id = request.args.get('gplace_id')
    detail = db.hospital_details.find_one({'gplace_id': gplace_id}, {'_id':0})
    if detail is None:
        detail = ad.insert_details_hospital(gplace_id)
        time.sleep(1)
    detail = db.hospital_details.find_one({'gplace_id': gplace_id}, {'_id':0})
    return jsonify({'result': detail})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)

# @app.route('/search', methods=['POST'])
# def search_places():
#     service_selection = str(request.form['service_selection'])
#     user_input = str(request.form['user_input'])
#     range_selection = float(request.form['range_selection'])
#     print("1: ", service_selection, user_input, range_selection)
#     if service_selection == "hospital":
#         # redirect to hospital listing page
#         print("2: ", service_selection, user_input, range_selection)
#         return redirect(url_for('tohospital'))
#     else:
#         # redirect to shelter listing page
#         return redirect('shelter.html', input=user_input, radius=range_selection)