from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request
from datetime import datetime

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
        gu=sorted(gu, key=(lambda x:x['review']),reverse=True)
        mode = 0

    elif filters == '동':
        dong = list(db.dbmyproject.find({'dong': {'$regex':keyword}},{'_id':False}))
        dong=sorted(dong, key=(lambda x:x['review']),reverse=True)

        mode = 1

    else:
        name = list(db.dbmyproject.find({'name': {'$regex': keyword}}, {'_id': False}))
        name=sorted(name, key=(lambda x:x['review']),reverse=True)

        mode = 2

    return jsonify({'result': 'success', 'gu': gu, 'dong':dong, 'name':name, 'mode':mode})


@app.route('/review', methods=['POST'])
def create_review():
    uid=int(request.form['uid'])
    reviewId=request.form['reviewId']
    content=request.form['content']
    time=datetime.now()
    db.dbmyprojectreview.insert_one(
        {
            'reviewId':reviewId,
            'content':content,
            'last_modified':time,
        }
    )
    db.dbmyproject.update_one({'uid': uid}, {'$inc': {'review': 1}})
    count=db.dbmyproject.find_one({'uid':uid}, {'_id':False})
    return jsonify({'result':'success', 'reviewId':reviewId, 'content':content, 'count':count})

@app.route('/reviews', methods=['GET'])
def show_review():
    review=request.args.get('reviewId')
    reviewList=list(db.dbmyprojectreview.find({'reviewId':review}, {'_id':False}))
    return jsonify({'result':'success', 'reviewList':reviewList})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)