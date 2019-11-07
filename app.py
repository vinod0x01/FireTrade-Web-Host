#importing libraries
import pyrebase
from flask import *
import json
import prediction_engine.Stock_Direction as sd
#importing payment library
import stripe

#setting the stripe variables
STRIPE_PUBLISHABLE_KEY = 'pk_test_9qnorLWUQILDlpMbGFjx1jM300ESwEvbGe'
STRIPE_SECRET_KEY = 'sk_test_AxJs3AsRcXNSw5kZ6RUr66Au00LLXE8ynD'

stripe.api_key = STRIPE_SECRET_KEY

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

dict_of_items = {}
#defining the companies for stock
_companies = {
    "FB": "FACEBOOK",
    "AAPL": "APPLE",
    "AMZN": "AMAZON",
    "NFLX": "NETFLIX",
    "GOOGL": "GOOGLE",
    "SBUX": "STARBUCKS",
    "XOM": "EXXON MOBILE",
    "JNJ": "JOHNSON & JOHNSON",
    "BAC": "BANK OF AMERICA",
    "GM": "GENERAL MOTORS"
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
    dict_of_items = None
    return redirect(url_for("index", msg="You have been logged out"))

#route for selector
@app.route("/selector")
@app.route("/selector<msg>")
def selector(msg=None):
    global _companies
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))
    return render_template('selector.html', itms=_companies, msg=msg)

#route for processing the selected list
@app.route("/submit_items", methods = ['GET','POST'])
def submit_items():
    global dict_of_items
    #check for user login
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))
    if request.method == 'POST':
        #get the dictionary of data
        data = request.form.to_dict()
        dict_of_items = data
        return jsonify({"result":"success", "url": url_for('predictor')})

#displaying the predicted
@app.route("/predictor")
def predictor():
    global dict_of_items
    #check for user login
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))

    if db.child("users").child(info['users'][0]['localId']).child("paid").get().val() == 0:
        return redirect(url_for("pay_money", msg="Please pay to continue"))

    if dict_of_items == None or not dict_of_items:
        return redirect(url_for('selector', msg="please select 5 stock to continue"))
    #get the payment recipt link
    recipt = db.child("users").child(info['users'][0]['localId']).child("payment").child("receipt_url").get().val()

    x = {}
    for i in dict_of_items.keys():
        x[dict_of_items[i]] = _companies[dict_of_items[i]]
    #get prediction from backend for next day stocks
    f_pred = sd.main_function(ticker_list=list(x.keys()))

    uname = db.child("users").child(info['users'][0]['localId']).child('name').get()
    uname = uname.val()

    return render_template('predict.html', msg=uname, s_list=x, pred=dict(f_pred), rec=recipt)

#payment methods
@app.route("/pay_money")
@app.route("/pay_money<msg>")
def pay_money(msg=None):
    #check for user login
    curr_user = auth.current_user
    if curr_user == None:
        return redirect(url_for('index', msg='login to continue'))

    if db.child("users").child(info['users'][0]['localId']).child("paid").get().val() == 1:
        return redirect(url_for("selector", msg="you have paid"))

    return render_template('payment.html', msg=msg)

@app.route("/pay", methods=['POST'])
def pay():

    #creating the cusromer and chage in stripe by paid user
    amount = 25000

    try:
        customer = stripe.Customer.create(
            email=request.form['stripeEmail'],
            source=request.form['stripeToken']
        )
        charge = stripe.Charge.create(
            amount=amount,
            currency='USD',
            customer=customer.id,
            description='payment for Fire Trade'
        )

        #saving data in firebase
        p_data = {
            "paid":charge["paid"],
            "amount":charge["amount"],
            "paid_mail":request.form['stripeEmail'],
            "currency":charge["currency"],
            "customer":charge["customer"],
            "description":charge["description"],
            "payment_method_details":charge["payment_method_details"],
            "receipt_url":charge["receipt_url"],
            "status":charge["status"]
        }
        db.child("users").child(info['users'][0]['localId']).update({"paid":1})
        db.child("users").child(info['users'][0]['localId']).child("payment").set(p_data)
        return redirect(url_for("predictor"))

    except Exception as e:
        print(str(e))
        return redirect(url_for('selector', msg='payment failed please try again'))

if __name__ == "__main__":
    app.debug = True
    app.run()
    app.run(debug=True)
