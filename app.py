from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
import certifi
import numpy as np
from PIL import Image
import os

import requests
from bs4 import BeautifulSoup

from pymongo import MongoClient

# model = tf.keras.models.load_model('static/model/first_training_data.h5')
# print("model roaded")


# client = MongoClient('mongodb+srv://test:sparta@cluster0.i0lgb.mongodb.net/test')
# db = client.dbprojects


# SY db 테스트용
client = MongoClient('mongodb+srv://test:sparta@cluster0.g1cco.mongodb.net/Cluster0?retryWrites=true&w=majority',tlsCAFile=certifi.where())
db = client.dbsidepj

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://music.bugs.co.kr/musicpd/albumview/39691', headers=headers)  # 기쁠 때
data2 = requests.get('https://music.bugs.co.kr/musicpd/albumview/50746', headers=headers)  # 화날 때
data3 = requests.get('https://music.bugs.co.kr/musicpd/albumview/50519', headers=headers)  # 짜증날 때
data4 = requests.get('https://music.bugs.co.kr/musicpd/albumview/41409', headers=headers)  # 무서울 때
data5 = requests.get('https://music.bugs.co.kr/musicpd/albumview/50793', headers=headers)  # 무표정일 때
data6 = requests.get('https://music.bugs.co.kr/musicpd/albumview/50839', headers=headers)  # 슬플 때
data7 = requests.get('https://music.bugs.co.kr/musicpd/albumview/44402?wl_ref=list_mab_01', headers=headers)  # 놀랄 때

data_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=6',headers=headers)  # 기쁠 때
data1_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=19',headers=headers)  # 화날 때
data2_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=15',headers=headers)  # 짜증날 때
data3_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=11',headers=headers)  # 무서울 때
data4_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=cur&date=20220113',headers=headers)  # 무표정일 때
data5_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=18',headers=headers)  # 슬플 때
data6_movie = requests.get('https://movie.naver.com/movie/sdb/rank/rmovie.naver?sel=pnt&date=20220113&tg=18',headers=headers)  # 놀랄 때

check = db.feeling_data.find_one({'feeling_num': 0})
if check is None:
    soup_happiness = BeautifulSoup(data.text, 'html.parser')
    soup_angry = BeautifulSoup(data2.text, 'html.parser')
    song_disgust = BeautifulSoup(data3.text, 'html.parser')
    song_fear = BeautifulSoup(data4.text, 'html.parser')
    song_neutral = BeautifulSoup(data5.text, 'html.parser')
    song_sad = BeautifulSoup(data6.text, 'html.parser')
    song_surprise = BeautifulSoup(data7.text, 'html.parser')

    soup_happiness_movie = BeautifulSoup(data_movie.text, 'html.parser')
    soup_angry_movie = BeautifulSoup(data1_movie.text, 'html.parser')
    song_disgust_movie = BeautifulSoup(data2_movie.text, 'html.parser')
    song_fear_movie = BeautifulSoup(data3_movie.text, 'html.parser')
    song_neutral_movie = BeautifulSoup(data4_movie.text, 'html.parser')
    song_sad_movie = BeautifulSoup(data5_movie.text, 'html.parser')
    song_surprise_movie = BeautifulSoup(data6_movie.text, 'html.parser')

    # 데이터
    emotion_musics = [soup_happiness.select('#ESALBUM39691 > table > tbody > tr'),
                      soup_angry.select('#ESALBUM50746 > table > tbody > tr'),
                      song_disgust.select('#ESALBUM50519 > table > tbody > tr'),
                      song_fear.select('#ESALBUM41409 > table > tbody > tr'),
                      song_neutral.select('#ESALBUM50793 > table > tbody > tr'),
                      song_sad.select('#ESALBUM50839 > table > tbody > tr'),
                      song_surprise.select('#ESALBUM44402 > table > tbody > tr'),
                      ]

    emotion_movies = [soup_happiness_movie,
                      soup_angry_movie,
                      song_disgust_movie,
                      song_fear_movie,
                      song_neutral_movie,
                      song_sad_movie,
                      song_surprise_movie
                      ]

    color = ['yellow', 'red', 'pink', 'black', 'gray', 'purple', 'blue']

    for i in range(7):
        print(f"{i}번째에 해당하는 감정의 노래 크롤링 시작")
        emotion = emotion_musics[i]
        img_list = []
        title_list = []
        singer_list = []

        # 노래데이터 넣기
        for detail_song in emotion:
            img = detail_song.select_one('td > a > img')['src']
            title = detail_song.select_one('th > p > a').text
            singer = detail_song.select_one('td > p > a').text

            img_list.append(img)
            title_list.append(title)
            singer_list.append(singer)

        emotion_movie = emotion_movies[i]
        print(f"{i}번째에 해당하는 감정의 노래 크롤링 완료")
        # 영화데이터 넣기
        print(f"{i}번째에 해당하는 감정의 영화 크롤링 시작")
        for detail_movie in emotion_movie:
            movie = {}
            movie_title = []
            movie_point = []
            movie_img = []
            movie_intro = []
            temp_urls = []
            movie_intro_title = []

            # 영화타이틀, 주소
            movie_title_list = detail_movie.select(
                '#old_content > table.list_ranking > tbody > tr > td.title > div.tit5 > a')
            for title in movie_title_list:
                movie_title.append(title.text)
                # 각 영화 주소
                temp_url = 'https://movie.naver.com'
                temp_url += title.attrs['href']
                temp_urls.append(temp_url)

            # 영화 이미지_10개만 크롤링
            idx = 0
            for url in temp_urls:
                if idx < 10:
                    movie_profile = requests.get(url, headers=headers)
                    movie_profile_soup = BeautifulSoup(movie_profile.text, 'html.parser')
                    movie_profile_img = movie_profile_soup.select_one(
                        '#container > #content > div.article > div.mv_info_area > div.poster > a > img')['src']  # 이미지
                    movie_img.append(movie_profile_img)
                    idx += 1
                else:
                    break

                movie['title'] = movie_title
                movie['img'] = movie_img

            # 영화 점수
            point_list = detail_movie.select('#old_content > table.list_ranking > tbody > tr > td.point')
            for point in point_list:
                movie_point.append(point.text)
            movie['point'] = movie_point
        print(f"{i}번째에 해당하는 감정의 영화 크롤링 완료")
        db.feeling_data.insert_one({
            'feeling_num': i,
            'color': color[i],
            'img': img_list,
            'title': title_list,
            'singer': singer_list,
            'movie': movie
            # 'chicken': chicken
        })
        print(f"{i}번째에 해당하는 감정의 데이터 저장 완료")
app = Flask(__name__)


@app.route('/')
def home():
    return render_template('first.html')


@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/result/api', methods=['POST'])
def result_api():
    # 이미지이기에, rescale 및 size 조정을 위해 ImageDataGenerator 활용
    # test_datagen = ImageDataGenerator(rescale=1. / 255)
    # test_dir = 'static/img/'     # test_dir에 폴더별로 사진을 저장 해야함
    #
    # test_generator = test_datagen.flow_from_directory(
    #     test_dir,
    #     target_size=(48, 48),
    #     shuffle=False,
    #     class_mode='categorical'
    # )
    # pred = model.predict(test_generator)[0].tolist()  # numpyarray를 list로 변환
    # # 마지막으로 업로드한 사진에 대한 판별결과를 보여줌
    # pred_sorted = []
    # for idx, val in enumerate(pred):
    #     pred_sorted.append((idx, val))  # 인덱스번호 부여
    # pred_sorted.sort(reverse=True, key=lambda x: x[1])  # 원래의 값을 기준으로 내림차순 정렬

    result = list(db.feeling_data.find({}, {'_id': False}))  # 임시로 모든 데이터를 넣었습니다!

    # fir_data = db.feeling_data.find_one({'feeling_num':pred_sorted[0][0]})  # 1번째로 높은 값 가져오기
    # result.append(fir_data)
    #
    # sec_data = db.feeling_data.find_one({'feeling_num':pred_sorted[1][0]})  # 2번째로 높은 감정의 값들 가져오기
    # result.append(sec_data)
    #
    # thd_data = db.feeling_data.find_one({'feeling_num':pred_sorted[2][0]})  # 3번째로 높은 감정의 값들 가져오기
    # result.append(thd_data)

    return jsonify({'result': result})


@app.route('/result/second')
def result_second():
    return render_template('second.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=False)
