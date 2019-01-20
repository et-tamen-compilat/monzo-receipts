from flask import Flask, render_template, request, session
import requests
import urllib.parse
import uuid
import config
import sqlite3
from lib import ReceiptsClient
app = Flask(__name__)
import dateutil.parser
from werkzeug.utils import secure_filename

app.config['SECRET_KEY'] = 'adsfjhdskljfhadklsjhfkljasdhfl'
app.config['UPLOAD_FOLDER'] = 'upload'

def process(x):
    return {"name": x["merchant"]["name"] if x["merchant"] != None else "Unknown" , "amount": x["amount"], "date": x["created"], "id": x["id"]}

@app.route("/")
def hello():
    if "id" in session:
        l = ReceiptsClient(session["access_token"])
        print(l.do_auth())
        if request.args.get("since"):
            trans = list(map(process, l.list_transactions(100, request.args.get("since"))))
        else:
            trans = list(map(process, l.list_transactions2(100)))
        m = None
        if len(trans) != 0:
          print(trans[-1])  
          m = trans[-1]["date"]
        return render_template("transactions.html", transactions=trans, m=m)
    else:    
        state = uuid.uuid4().hex
        client_id = config.MONZO_CLIENT_ID
        u = urllib.parse.quote_plus(config.MONZO_OAUTH_REDIRECT_URI)
        url = "https://auth.monzo.com/?client_id=" + client_id + "&redirect_uri=" + u + "&response_type=code&state=" + state
        return render_template("login.html", url=url)

@app.route("/doit/<transaction_id>")
def hello3(transaction_id):
    if "id" in session:
        l = ReceiptsClient(session["access_token"])
        result = l.doit(transaction_id)
        return "Success: " + str(result)
    else:    
        return "Authentication failed"

@app.route("/authenticate")
def hello2():
    print(request.args.get("code"))
    dic = {'grant_type':"authorization_code", 'client_id':config.MONZO_CLIENT_ID, 'client_secret':config.MONZO_CLIENT_SECRET, 'redirect_uri':"http://127.0.0.1:5000/authenticate", 'code':request.args.get("code")}
    print(dic)
    r = requests.post('https://api.monzo.com/oauth2/token', dic) 
    json_data = r.json()
    print(r.json())
    data = sqlite3.connect('data')
    c = data.cursor()
    c.execute('insert into session (access_token, refresh_token, user_id) values (?,?,?)',(json_data["access_token"], json_data["refresh_token"], json_data["user_id"]))
    session['id'] = c.lastrowid
    session['access_token'] = json_data["access_token"]
    return "Authentication successful"

@app.route('/', methods=['GET', 'POST'])
@app.route("/upload/<transaction_id>")
def upload_file():
    if 'file' not in request.files:
        return "no file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

