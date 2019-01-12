from flask import Flask, request, url_for, render_template
from flask import jsonify, session, current_app
from flask_restful import reqparse, abort, Api, Resource
from flask_cors import CORS, cross_origin
import json
import requests
import random
import os
import logging
import re
import pdb
import pickle


logging.basicConfig(format='%(asctime)s %(message)s',
 datefmt='%m/%d/%Y %I:%M:%S %p',
 filename='modelMBA.log',
 level=logging.DEBUG)

app = Flask(__name__)
# the directory of the curent file
working_dir = os.path.dirname(os.path.abspath(__file__))
with open(working_dir+os.sep+'k.txt') as f:
    k = f.read()
content = k.strip()

app.secret_key = content

#api
api = Api(app)
#cors for cross origin headers
CORS(app)

# the directory of the curent file
working_dir = os.path.dirname(os.path.abspath(__file__))
# the data folder
data_folder_path = working_dir + os.sep + "models"

"""
LyricalApi class takes a GET request
parses the keys, if the artist key is present
look up random lyric from said artist
if its not, look up random lyric from Cardi B

TODO: use jsonify instead of this weird lil custom dictionary thing, no?
"""
class ModelMBAApi(Resource):
    def post(self):
        json_data = request.get_json()

        school = json_data['school']

        school_model = load_model(school)

        chance = find_my_chances(
            school = school_model,
            gpa=json_data['gpa'],
            gmat=json_data['gmat'],
            age=json_data['age'],
            race=json_data['race'],
            university=json_data['university'],
            major=json_data['major'],
            gender=json_data['male'])

def load_model(school):
    """
    Load model for a particular school from local filesystem
    """




def find_my_chances(school,gpa,gmat,age,race,university,major,gender):

    # create list of strings to trigger the applicant profile parsing
    gpa_str = "{} GPA".format(gpa)
    gmat_str = "{} GMAT".format(gmat)
    demo_str = "{a} year old {r} {g}".format(a=age,r=race,g=gender)
    school_info = "Degree in {m} at {uni} (University)".format(m=major,uni=university)

    app_profile = [gpa_str,gmat_str,demo_str,school_info]
    odds = ""
    for school in TARGET_LABELS:
        odds += "{}: 0.0\n".format(school)
    ap = ApplicantProfile(app_profile,odds)



    d = {}
    d["GMAT"] = ap.gmat_score
    d["GPA"] = ap.gpa
    d["UNIVERSITY"] = ap.uni
    d["MAJOR"] = ap.major
    d["JOBTITLE"] = ap.job_title
    d["GENDER"] = ap.gender
    d["RACE"] = ap.race
    d["AGE"] = ap.age
    d["INTERNATIONAL"] = ap.international
    d["ODDS"] = ap.odds.encode('utf-8').strip()

    df = pd.DataFrame(d,index=[0])
    schooldata_dict,mycolnames = preprocess_data(df)


    print("\n {d}".format(d=d))
    for school,indf in schooldata_dict.items():

        # if missing any columns from training set, add them w/ dummy vals
        for col in colnames:
            if col not in indf['features'].columns:
                indf['features'][col] = 0.0


        features_df = indf['features'][colnames]

        #print(features_df)


        df2predictfrom = features_df.values
        df2predictfrom = np.delete(df2predictfrom,0,axis=1)

        chance = MODELS[school].predict(df2predictfrom)
        try:
            pass
            #print("Coefficients: {}".format(MODELS[school].coef_))
        except AttributeError as ae:
            continue

        if school in ['Harvard','Wharton','Stanford','Booth']:
            print("{s} odds: {c}".format(s=school,c=chance))





@app.route('/')
def hello_world():
    return render_template('index.html')
    #return 'Hello You Have Reached The Cardi B Lyrics Api, send a get request to "cardibbars.pythonanywhere.com/api/v1"!'



api.add_resource(ModelMBAApi, '/api/v1')


if __name__ == "__main__":
    app.run(threaded=True)
