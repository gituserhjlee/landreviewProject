import requests
from pymongo import MongoClient

client = MongoClient('mongodb://test:test@localhost', 27017)
db = client.dbmyproject



def insert_info(url,index):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

    response_data = requests.get(url, headers=headers)
    land_info = response_data.json()
    rows = land_info['landBizInfo']['row']
    for row in rows:

        gu = row['SGG_NM']
        dong = row['BJDONG_NM']
        address = row['ADDRESS']
        name = row['CMP_NM']
        tel = row['TELNO']
        status = row['STS_GBN']

        db.dbmyproject.insert_one({'uid': index,
                                   'gu': gu,
                                   'dong': dong,
                                   'address': address,
                                   'name': name,
                                   'tel': tel,
                                   'status': status,
                                   'review' : 0
                                   })

        index+=1

    return index


def insert_all():
    index,start, end =0, 1, 1000
    url = 'http://openapi.seoul.go.kr:8088/54776c67746c686a35315442777579/json/landBizInfo/' + str(start) + '/' + str(
        end) + '/'
    db.dbmyproject.drop()
    index=insert_info(url,index)
    for i in range(25):
        start += 1000
        end += 1000
        url = 'http://openapi.seoul.go.kr:8088/54776c67746c686a35315442777579/json/landBizInfo/' + str(
            start) + '/' + str(end) + '/'
        index=insert_info(url,index)


insert_all()
