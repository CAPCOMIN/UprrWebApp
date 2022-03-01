# -*- coding:utf-8 -*-
from flask import Flask
from flask import render_template

import userWordCould
# import portraitDao

app = Flask(__name__)

@app.route('/')
def all():
    # data = portraitDao.getData()
    return '✔🍖🍗🥩🍠🥟🥠开启探索用户画像的大门😎'

@app.route('/portrait/')
@app.route('/portrait/<name>')
def portrait(name=None):
    wc = userWordCould.WC()
    wc.draw_wordcloud()
    return render_template('portrait.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)
    # app.run(debug=True,host='192.168.1.18')