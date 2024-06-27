from flask import Flask, redirect, url_for, render_template, request, jsonify, flash
from db_handler import DBModule
from bs4 import BeautifulSoup
import requests
import bcrypt
import json
import re

app = Flask(__name__)
app.secret_key = "dlrpantmsrlsmddmfgksmswldkfdkqhkdirpTek"
DB = DBModule()

# 부산대 맞춤법 검사기 URL
SPELL_CHECK_URL = 'http://speller.cs.pusan.ac.kr/results'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-spell', methods=['POST'])
def check_spell():
    # form에서 데이터 가져오기
    origin_text = request.form['text']

    # 크롤링할 때 필요한 값 설정
    data = {
        'text1': origin_text
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # HTTP POST 맞춤법 검사
    response = requests.post(SPELL_CHECK_URL, headers=headers, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')

    # script부분 추출
    scripts = soup.find_all('script')
    json_data = None

    # 여러 scripts 중 'data = []' 으로 된 부분 찾기
    for script in scripts:
        if script.string and 'data = [{' in script.string:
            match = re.search(r'data = (\[.*?\]);', script.string, re.DOTALL)
            if match:
                json_text = match.group(1)
                json_data = json.loads(json_text)
                break

    # json_data 프론트로 보내기
    if json_data:
        error_words = [error for result in json_data for error in result['errInfo']]
        return jsonify({'success': True, 'data': error_words})
    else:
        return jsonify({'success': False, 'message': 'Failed to retrieve JSON data'})

@app.route('/posts/<string:pid>/check-password', methods=['POST'])
def check_post_password(pid):
    post = DB.get_post(pid)
    password = request.form['password'].encode('utf-8')
    hashed_password = post['password'].encode('utf-8')

    if bcrypt.checkpw(password, hashed_password):
        return jsonify({'success': True, 'message': 'Password is correct'})
    else:
        return jsonify({'success': False, 'message': 'Password is not correct'})
    
@app.route('/posts/<string:pid>/comments/check-password', methods=['POST'])
def check_comment_password(pid):
    post = DB.get_post(pid)
    password = request.form['password']
    return 

@app.route('/posts', methods=['GET'])
def get_posts():
    posts = DB.get_posts()
    return render_template('posts.html', posts=posts.items())

@app.route('/post/new', methods=['POST'])
def push_post():
    title = request.form['title']
    content = request.form['content']
    password = request.form['password']
    pid = DB.push_post(title, content, password)
    return jsonify({'success': True, 'pid': pid})

@app.route('/post/new', methods=['GET'])
def get_post_write():
    return render_template('post_new.html')

@app.route('/posts/<string:pid>', methods=['GET'])
def get_post(pid):
    post = DB.get_post(pid)
    return render_template('post.html', post=post, pid=pid)

@app.route('/posts/<string:pid>/edit', methods=['GET'])
def get_post_edit(pid):
    return render_template('post_edit.html')

@app.route('/posts/<string:pid>/edit', methods=['PUT'])
def update_post(pid):
    pass

@app.route('/posts/<string:pid>/delete', methods=['DELETE'])
def remove_post(pid):
    pass

@app.route('/posts/<string:pid>/comments', methods=['GET'])
def get_comments(pid):
    pass

@app.route('/posts/<string:pid>/comments/new', methods=['POST'])
def push_comments(pid):
    pass

@app.route('/posts/<string:pid>/comments/<string:cid>/edit', methods=['PUT'])
def update_comment(pid, cid):
    pass

@app.route('/posts/<string:pid>/comments/<string:cid>/delete', methods=['DELETE'])
def remove_comment(pid, cid):
    pass

if __name__ == '__main__':
    app.run(debug=True)

