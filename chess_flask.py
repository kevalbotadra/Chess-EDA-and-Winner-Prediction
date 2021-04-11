# Import neccesary packages
import pandas as pd
import numpy as np
from flask import Flask, render_template, request
import pickle
from chessdotcom import get_player_stats
import pprint
from sklearn.preprocessing import MinMaxScaler, normalize, LabelEncoder, scale
from fuzzywuzzy.process import extractOne

# Data Encoder Processing

df = pd.read_csv("games.csv")
for i in range(df.shape[0]):
    if df.iloc[i].winner == "white":
        df["winner"][i] = 0
    elif df.iloc[i].winner == "black":
        df["winner"][i] = 1
    else:
        df["winner"][i] = 2
X = df[["rated", "white_rating", "black_rating", "opening_name"]]
X.head()
y = df["winner"]
y=y.astype('int')
print(y.head())


all_opening_names = X.opening_name.values



rated_encoder = LabelEncoder()
white_encoder = LabelEncoder()
black_encoder = LabelEncoder()
opening_encoder = LabelEncoder()
winner_encoder = LabelEncoder()

X["rated"] = rated_encoder.fit_transform(X["rated"])
X["white_rating"] = white_encoder.fit_transform(X["white_rating"])
X["black_rating"] = black_encoder.fit_transform(X["black_rating"])
X["opening_name"] = opening_encoder.fit_transform(X["opening_name"])


# Initiate the flask app
app = Flask(__name__)


# Define the printer class
printer = pprint.PrettyPrinter()

# Define the function to obtain ratings
def get_player_ratings(username):
    data = get_player_stats(username).json
    printer.pprint(data)
    categories = ["chess_blitz", "chess_rapid", "chess_bullet"]
    for category in categories:
        print("Category:", category)
        try:
            print(f'Current: {data["stats"][category]["last"]["rating"]}')
        except:
            print("No Current Value Available")
        try:
            print(f'Best: {data["stats"][category]["best"]["rating"]}')
        except:
            print("No Best Value Available")

# Define the Loading Model Function

def load_model():
    filename = 'chess_winner_prediction.sav'
    with open(filename, "rb") as file:
        model = pickle.load(file)
    
    return model

model = load_model()

# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Prediction Page
@app.route("/predict", methods=["POST"])
def predict():
    print(request.form.values())
    X = []
    for feature in request.form.values():
        try:
            X.append(int(feature))
        except:
            X.append(feature)
    
    if X[0] == "on":
        X[0] = True
    else:
        X[0] = False
    
    opening_move_name = extractOne(X[3], all_opening_names)
    X[3] = opening_move_name[0]

    print(X)

    X = pd.DataFrame({"rated" : X[0], "white_rating" : X[1], "black_rating" : X[2], "opening_name" : X[3]}, index=[0])
    X["rated"] = rated_encoder.transform(X["rated"])
    X["white_rating"] = white_encoder.transform(X["white_rating"])
    X["black_rating"] = black_encoder.transform(X["black_rating"])
    X["opening_name"] = opening_encoder.transform(X["opening_name"])
    X = np.array(X)
    chess_winner_classes = ["white", "black", "draw"]
    chess_prediction = model.predict(X)[0]
    winner = chess_winner_classes[chess_prediction]
    return render_template("index.html", prediction_text="The winner of this match is most likely going to be {}!".format(winner))



if __name__ == "__main__":
    app.run(debug=True)