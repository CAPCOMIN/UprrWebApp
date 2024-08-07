# -*- coding: UTF-8 -*-
# Setting path variables
import sys
import pandas as pd
from configs import *
import generateWordcloud
from PreProcessing import utils

sys.path.append(PROJECT_PATH)

# Importing required libraries
from flask import Flask, render_template, request
from cfaGenerator.generator import RecommendationGenerator

VERSION = "2.0.0 Release 22031"

features, data = RecommendationGenerator.load_data(RecommendationGenerator, datapath=DATA_PATH)
users = data['userID'].unique()

app = Flask(__name__)


# HomePage
@app.route("/")
def home():
    return render_template("index.html", version=VERSION, max=users.shape[0])


# ResultPage
@app.route("/result", methods=["GET", "POST"])
def result():
    if request.method == "POST":

        # Collecting the form responses
        userdata = request.form

        # Extracting the values for UserIndex and No. of recommendations
        user = int(userdata.get("index"))
        N = int(userdata.get("N"))

        # Getting the userID from the user Index
        users = data['userID'].unique()
        userID = int(users[user])

        # Running the model, generating recommendations and passing the list to the HTML page
        model = RecommendationGenerator(userID, N)
        recomm = model.generate_recommendations(features, data)

        fcm = open("tmp/tmp_cossim_mat.txt", "r")
        scm = fcm.read()
        lcm = scm.split(',')
        lcm = lcm[0:253]
        fcm.close()

        fri = open("tmp/tmp_recomm_indices.txt", "r")
        sri = fri.read()
        lri = sri.split('\n')
        fri.close()

        return render_template("result.html", userID=userID - 1, rec_list=recomm, cm_list=lcm, ri_list=lri)

    else:

        return "Sorry, there was an error."


# SearchPage
@app.route("/search")
def search():
    return render_template("search.html", max=users.shape[0])


# SearchResultPage
@app.route("/searchresult", methods=["GET", "POST"])
def searchresult():
    if request.method == "POST":

        # Collecting the form responses
        userdata = request.form
        print(userdata)

        if list(userdata)[0] == 'manufacturer':
            course = userdata.get("manufacturer")
            data = pd.read_csv(DATA_PATH, usecols=['courseID', 'userID'])
            studentSearchResult = data[data['courseID'] == course]
            print(studentSearchResult)
            return render_template("searchresult.html", ID=course, rec_list=studentSearchResult['userID'].to_list())

        else:

            # Extracting the values for UserIndex and No. of recommendations
            user = int(userdata.get("index"))

            # Loading courseID and userID data and converting userID from type object to numeric
            # 加载 courseID 和 userID 数据并将 userID 从类型对象转换为数字
            data = pd.read_csv(DATA_PATH, usecols=['courseID', 'userID'])
            # cols = data.columns.drop('userID')
            data['userID'] = data['userID'].apply(pd.to_numeric, errors='coerce')
            data = data.fillna(0)

            courseSearchResult = data[data['userID'] == user]
            # searchResult = searchResult.columns.drop('userID')
            print(courseSearchResult)
            return render_template("searchresult.html", ID=user, rec_list=courseSearchResult['courseID'].to_list())

    else:
        return "Sorry, there was an error in searchResult."


# SearchPortraitPage
@app.route("/searchportrait")
def searchportrait():
    return render_template("/searchportrait.html", max=users.shape[0])


# UserPortraitPage
@app.route("/userportrait", methods=["GET", "POST"])
def userportrait():
    if request.method == "POST":

        # Collecting the form responses
        userdata = request.form

        # Extracting the values for UserIndex and No. of recommendations
        user = int(userdata.get("index"))

        # Loading courseID and userID data and converting userID from type object to numeric
        # 加载 courseID 和 userID 数据并将 userID 从类型对象转换为数字
        data = pd.read_csv(DATA_PATH, usecols=['courseID', 'userID', 'courseFeature'])
        # cols = data.columns.drop('userID')
        data['userID'] = data['userID'].apply(pd.to_numeric, errors='coerce')
        # data = data.fillna(0)
        data.dropna(axis=0, how='any', inplace=True)
        userportrait = data[data['userID'] == user]
        # userportrait = userportrait.columns.drop('userID')
        print(userportrait)

        featureList = userportrait['courseFeature'].to_list()

        # 写入课程 features 以生成画像
        f = open("features.txt", "a")
        f.truncate(0)
        for i in featureList:
            c = i.split(',')
            for ci in c:
                print(ci)
                f.write(ci + "\n")
        f.close()
        freq = {}
        try:
            wc = generateWordcloud.WC()
            freq = wc.draw_wordcloud()
        except ValueError:
            print(ValueError)
            return render_template("userportrait.html", userID=user, rec_list=["⚠", ValueError, "WordCould ValueError"],
                                   freq_dict=["⚠", ValueError, "WordCould ValueError"])
        # print(freq)

        return render_template("userportrait.html", userID=user, rec_list=featureList, freq_dict=freq)

    else:
        return "Sorry, there was an error in user portrait web app."


if __name__ == "__main__":
    app.run(debug=True)
