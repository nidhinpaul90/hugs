import os
import time
from flask_session import Session
from flask import Flask, render_template, abort, request, session, app
from flask import flash, redirect, url_for, json
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from time import sleep
from datetime import timedelta
import requests

keeper = time.time()
keeper0 = time.time()
app = Flask(__name__)
status = 0
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = 'secretkey00'
Session(app)


engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
mentionflag=0
msgflag=0
ip_ban_list = ['103.224.182.212', '10.1.90.119','10.1.82.90', '10.1.49.29', '10.1.88.135', '10.1.85.234', '10.1.82.205']


def is_human(captcha_response):
    """ Validating recaptcha response from google server
        Returns True captcha test passed for submitted form else returns False.
    """
    secret = "6LeMyJ0cAAAAAE3RNcsVxPuRV6GZA_GiMx04HXXT"
    payload = {'response':captcha_response, 'secret':secret}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_text = json.loads(response.text)
    print(response_text)
    return response_text['success']

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)
    try:
        ip = request.remote_addr
    except:
        ip = ['999.999.999.999']

    if ip in ip_ban_list:
        abort(403)

@app.route("/", methods=["GET", "POST"])
def index():
    sitekey = '6LeMyJ0cAAAAANIokl_HO3phHua9-C7MG0laOzwI'
    if session.get('ip') is None:
        session['ip'] = request.environ['REMOTE_ADDR']
    if session.get('captcha_response') is None:
        session['captcha_response'] = ""

    global mentionflag, msgflag, keeper, keeper0
    status=0


    if session.get('value') is None:
        session['value'] = 0
    if request.method == "POST":
        status = 0
        session['captcha_response'] = request.form['g-recaptcha-response']
        msg= request.form.get("name")
        if session['value'] >= 3:
            status=6
            return render_template("index.html", status=status, sitekey=sitekey)
        if is_human(session['captcha_response']):
            print('human verified')
        else:
             status=99
             return render_template("index.html", status=status, sitekey=sitekey)


        session['value'] += 1


        if "@" in msg:
            mentionflag += 1

        if mentionflag == 5:
            keeper=time.time()

        if mentionflag >= 5:
            keeper2 = time.time()
            diff = keeper2 - keeper
            if diff > 1800:
                mentionflag=0
            if mentionflag == 0:
                print('awoken')

        if mentionflag >=5:
            status=5
            return render_template("index.html", status=status, sitekey=sitekey)




        if "https://" in msg:
            status=2
            return render_template("index.html", status=status, sitekey=sitekey)


        msgflag += 1

        if msgflag ==15:
            keeper0 = time.time()


        if msgflag >= 15:

            keeper3 = time.time()
            diff2 = keeper3 - keeper0
            if diff2 > 1800:
                msgflag=0
            if msgflag == 0:
                print('awoken')

        if msgflag >= 15:
            status=10
            return render_template("index.html", status=status, sitekey=sitekey)





        if msg == "":
            status=2
            return render_template("index.html", status=status, sitekey=sitekey)
        db.execute("INSERT INTO operation (msg, ip) VALUES (:msg, :ip)",
                {"msg": msg, "ip": session['ip']})
        db.commit()
        status=1

    return render_template("index.html", status=status, sitekey=sitekey)
