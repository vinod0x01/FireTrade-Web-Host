#importing libraries
import pyrebase
from flask import *
import json
import prediction_engine.Stock_Direction as sd
#defining the firebase configurations from created app int he firebase
config = {
    "apiKey": "AIzaSyDr-4uZw1snFiOg26eQC7VOsvUPYCB3zVU",
    "authDomain": "test-72921.firebaseapp.com",
    "databaseURL": "https://test-72921.firebaseio.com",
    "projectId": "test-72921",
    "storageBucket": "",
    "messagingSenderId": "433457544866",
    "appId": "1:433457544866:web:4a5047b20c2e1a85f4a1fb",
    "measurementId": "G-11B51GZLZ0"
  }

#initialising the firebase authentiCATION methods
firebase = pyrebase.initialize_app(config)

#initialising auth
auth = firebase.auth()

#initialising the firebase database
db = firebase.database()

#initialize user
user = None
info = None
#initialising the flask app
app = Flask(__name__)

list_of_items = {}
#defining the companies for stock
_companys = {
    "FB": "FACEBOOK",
    "AAPL": "APPLE",
    "AMZN": "AMAZON",
    "NFLX": "NETFLIX",
    "GOOGL": "GOOGLE",
    "SBUX": "STARBUCKS",
    "XOM": "EXXON MOBILE",
    "JNJ": "JHONSON & JHONSON",
    "BAC": "BANK OF AMERICA",
    "GM": "GENARAL MOTORS"
    }
#route web page to log in
@app.route("/")
@app.route("/<msg>")
def index(msg=None):
    return render_template('index.html', msg=msg)

#verification route
@app.route("/login", methods = ['GET','POST'])
def login():
    global user, info
    if request.method == 'POST':
        #get the data from jscript
        data = request.form.to_dict()

        #sign in with the email and pasword entered
        try:
            user = auth.sign_in_with_email_and_password(data['email'], data['password'])
            info = auth.get_account_info(user['idToken'])
            if (info['users'][0]['emailVerified']):
                return jsonify({"result":"success", "url": url_for('selector')})
            else:
                raise Exception("[] {'error':{'error':'Manual', 'message':'Please verify email to login'}}")
        except Exception as e:
            try:
                emsg = str(e)
                x = emsg.find(']')
                emsg = eval(emsg[x+2:])
                return jsonify({"result": "failed", "msg":str(emsg['error']['message']).replace('_', ' ')})
            except Exception as e:
                return jsonify({"result": "failed", "msg":str(e)})

#route for sign in template
@app.route("/sign_in", methods=['GET'])
def sign_in():
    return render_template("sign_in.html")

#route for creating the new user
@app.route("/create_user", methods=['GET','POST'])
def create_user():
    global user, info
    if request.method == 'POST':
        #get the data from javascript
        data = request.form.to_dict()

        #create a user with the email and password
        try:
            user = auth.create_user_with_email_and_password(data['email'], data['password'])
            info = auth.get_account_info(user['idToken'])
            p_data = {
                "name": data["name"],
                "paid": 0
            }

            db.child("users").child(info['users'][0]['localId']).set(p_data)

            result = auth.send_email_verification(user['idToken'])
            return jsonify({"result": "success", "msg":str(result['email'])})

        except Exception as e:
            #processing the error
            try:
                emsg = str(e)
                x = emsg.find(']')
                emsg = eval(emsg[x+2:])
                return jsonify({"result": "failed", "msg":str(emsg['error']['message']).replace('_', ' ')})
            except Exception as _e:
                print(str(_e))
                print(str(e))
                return jsonify({"result": "failed", "msg":str(_e).replace('_', ' ')})
#logout
@app.route("/logout_")
def logout():
    auth.current_user=None
    return redirect(url_for("index", msg="You have been logged out"))

#route for selector
@app.route("/selector")
def selector():
    global _companys
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))
    return render_template('selector.html', itms=_companys)

#route for processing the selected list
@app.route("/submit_items", methods = ['GET','POST'])
def submit_items():
    global list_of_items
    #check for user login
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))
    if request.method == 'POST':
        #get the dictionary of data
        data = request.form.to_dict()
        list_of_items = data
        return jsonify({"result":"success", "url": url_for('predictor')})

#displaying the predicted
@app.route("/predictor")
def predictor():
    global list_of_items
    #check for user login
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))
    x = {}
    for i in list_of_items.keys():
        x[list_of_items[i]] = _companys[list_of_items[i]]
    #get prediction from backend for next day stocks
    f_pred = sd.main_function(ticker_list=list(x.keys()))

    uname = db.child("users").child(info['users'][0]['localId']).child('name').get()
    uname = uname.val()

    return render_template('predict.html', msg=uname, s_list=x, pred=dict(f_pred))

if __name__ == "__main__":
    app.debug = True
    app.run()
    app.run(debug=True)
