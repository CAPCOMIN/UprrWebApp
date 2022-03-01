# Setting path variables
import sys
import pandas as pd
from configs import *
from Input_Preprocessing import utils

sys.path.append(PROJECT_PATH)

# Importing required libraries
from flask import Flask, render_template, request
from Recommendation_Generator.generator import recommendationGenerator

features, data = recommendationGenerator.load_data(recommendationGenerator, datapath=DATA_PATH)
users = data['userID'].unique()

app = Flask(__name__)


# HomePage
@app.route("/")
def home():
    return render_template("index.html", max=users.shape[0] - 1)


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
        model = recommendationGenerator(userID, N)
        recomm = model.generate_recommendations(features, data)

        return render_template("result.html", userID=userID, rec_list=recomm)

    else:

        return "Sorry, there was an error."


# SearchPage
@app.route("/search")
def search():
    return render_template("search.html", max=users.shape[0] - 1)


# SearchResultPage
@app.route("/searchResult", methods=["GET", "POST"])
def searchResult():
    if request.method == "POST":

        # Collecting the form responses
        userdata = request.form

        # Extracting the values for UserIndex and No. of recommendations
        user = int(userdata.get("index"))

        # Loading courseID and userID data and converting userID from type object to numeric
        # 加载 courseID 和 userID 数据并将 userID 从类型对象转换为数字
        data = pd.read_csv(DATA_PATH, usecols=['courseID', 'userID'])
        # cols = data.columns.drop('userID')
        data['userID'] = data['userID'].apply(pd.to_numeric, errors='coerce')
        data = data.fillna(0)

        searchResult = data[data['userID'] == user]
        # searchResult = searchResult.columns.drop('userID')
        print(searchResult)
        return render_template("result.html", userID=user, rec_list=searchResult['courseID'].to_list())

    else:

        return "Sorry, there was an error."


if __name__ == "__main__":
    app.run(debug=True)
