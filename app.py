from pymongo import MongoClient

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbmyproject

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/land', methods=['POST'])
def show_result():
    gu, dong, name='데이터 없음','데이터 없음','데이터 없음'

    filters = request.form['opt']
    keyword = request.form['keyword']
    # list(db.dbmyproject.find({"$or":[{'gu': {'$regex':keyword}}, {'dong':{'$regex':keyword}},{'name':{'$regex':keyword}}]})) #필터없이 or로 검색할때
    if filters == '구':
        gu = list(db.dbmyproject.find({'gu': {'$regex': keyword}}, {'_id': False}))
        mode = 0
    elif filters == '동':
        dong = list(db.dbmyproject.find({'dong': {'$regex':keyword}},{'_id':False}))
        mode = 1

    else:
        name = list(db.dbmyproject.find({'name': {'$regex': keyword}}, {'_id': False}))
        mode = 2


    return jsonify({'result': 'success', 'gu': gu, 'dong':dong, 'name':name, 'mode':mode})

@app.route('/review.html')
def show_review():
    return render_template('review.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)