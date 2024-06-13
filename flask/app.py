import os
import re
from flask import Flask , render_template, send_from_directory,request,redirect,url_for,session
from flask_session import Session
from elasticsearch import Elasticsearch


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
client = Elasticsearch(
  "https://localhost:9200",
  http_auth=("elastic", "D8DQM05DKQPBG08_Iy3Y"),
  ca_certs=False,
  verify_certs=False
)
Session(app)
 

@app.route('/')
def home():
    
    print(client.info())

    if not session.get("results"):
        session["results"]=[]
    if not session.get("msg"):
        session["msg"]="Read What People Say Before Decide Your Next Meal"

    results=session["results"]
    msg=session["msg"]
    return render_template('home.html',results=results,msg=msg)

@app.route('/submit',methods=['POST'])
def submit():
    search_term =  request.form['form-search']
    
    query={
        "multi_match":{
         "query":search_term,
         "fields":["food_name","keywords"],
         "operator":"or",
         "type":"best_fields",
         "fuzziness":"AUTO"
      }
    }
    sort=[
        {
            "shops.overall_sentimental_rating": {
                "order": "desc"
            }
        }
    ]
    response = client.search(index="food",query=query,sort=sort,size=1)
    print(response["hits"]["hits"])
    session["results"]=response["hits"]["hits"]
    session["msg"]="Enjoy "+search_term
    return redirect(url_for('home'))
        


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'templates'),
                          'favicon.ico',mimetype='image/vnd.microsoft.icon')

@app.route('/styles.css')
def styles():
    return send_from_directory(os.path.join(app.root_path, 'templates'),
                          'styles.css',mimetype='text/css')

if __name__ == '__main__':
    app.run(debug=True)