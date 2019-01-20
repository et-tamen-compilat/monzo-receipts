from flask import Flask, render_template, request, session
import requests
import urllib.parse
import uuid
import config
import sqlite3
app = Flask(__name__)


app.config['SECRET_KEY'] = 'adsfjhdskljfhadklsjhfkljasdhfl'

@app.route("/")
def hello():
    if "id" in session:
        return "Authenticated"
    else:    
        state = uuid.uuid4().hex
        client_id = config.MONZO_CLIENT_ID
        u = urllib.parse.quote_plus(config.MONZO_OAUTH_REDIRECT_URI)
        url = "https://auth.monzo.com/?client_id=" + client_id + "&redirect_uri=" + u + "&response_type=code&state=" + state
        return render_template("login.html", url=url)

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
    return "Authentication successful"


