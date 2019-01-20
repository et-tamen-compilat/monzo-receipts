from flask import Flask, render_template, request
import urllib.parse
import uuid
import config
app = Flask(__name__)

@app.route("/")
def hello():
    state = uuid.uuid4().hex
    client_id = config.MONZO_CLIENT_ID
    u = urllib.parse.quote_plus(config.MONZO_OAUTH_REDIRECT_URI)
    url = "https://auth.monzo.com/?client_id=" + client_id + "&redirect_uri=" + u + "&response_type=code&state=" + state
    return render_template("login.html", url=url)

@app.route("/authenticate")
def hello2():
    print(request.args.get("code"))
    return "Authentication successful"

