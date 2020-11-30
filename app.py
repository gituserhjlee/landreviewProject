import jwt
import datetime
import hashlib
from functools import wraps
from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request, redirect, url_for, g

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.dbmyproject
index=0
userindex=0
# jwt secret key
SECRET_KEY = 'hello world'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 쿠키에서 token_give 가져오기
        token_receive = request.cookies.get('token_give')
        print('token_receive :', token_receive)

        if token_receive is not None:
            try:
                # secret key를 이용하여 디코딩
                payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            except jwt.InvalidTokenError:
                # 토큰이 만료되었거나 올바르지 않은 경우 로그인 페이지로 이동
                return redirect(url_for('login'))

            # global 변수에 유저 정보를 추가
            g.user = db.user.find_one({'id': payload["id"]})
        else:
            # 토큰이 없는 경우 login 페이지로 이동
            return redirect(url_for('login'))

        # 로그인 성공시 다음 함수 실행
        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

# 회원가입
@app.route('/api/register', methods=['POST'])
def api_register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    # pw를 sha256 방법(단방향)으로 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    global userindex
    db.user.insert_one({'uid':userindex ,'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
    userindex+=1
    return jsonify({'result': 'success'})

# 로그인
@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    # pw를 sha256 방법(단방향)으로 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # id, 암호화된 pw을 가지고 해당 유저를 찾기
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        # jwt 토큰 발급
        payload = {
            'id': id_receive,  # user id
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10)  # 만료 시간 (10초 뒤 만료)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': 'Please check your id and password 😓'})


# 유저 닉네임 조회
@app.route('/api/nickname', methods=['GET'])
@login_required
def api_valid():
    return jsonify({'result': 'success', 'nickname': g.user['nick']})



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
    global index
    reviewuid = index
    index+=1
    reviewId=request.form['reviewId']
    content=request.form['content']
    time=datetime.datetime.now()
    time=time+datetime.timedelta(hours=9)

    db.dbmyprojectreview.insert_one(
        {
            'reviewuid':reviewuid,
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

@app.route('/deleteReview',methods=['DELETE'])
def delete_review():
    uid=int(request.form['uid'])
    reviewuid=int(request.form['reviewuid'])
    print(uid,reviewuid)

    db.dbmyprojectreview.delete_one({'reviewuid': reviewuid})
    db.dbmyproject.update_one({'uid': uid}, {'$inc': {'review': -1}})

    return jsonify({'result':'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)