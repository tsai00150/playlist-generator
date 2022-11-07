from flask import Flask, redirect, render_template, request, session, url_for
import os
from sqlalchemy import *

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

DATABASEURI = "postgresql://th2990:jz3581@w4111.cisxo09blonu.us-east-1.rds.amazonaws.com/proj1part2"
engine = create_engine(DATABASEURI)
conn = engine.connect()


@app.route('/')
def home(): 
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('homepage'))

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'p' and request.form['username'] == 'a':
        session['logged_in'] = True
        session['username'] = 'a'
        session['password'] = 'p'
        return redirect(url_for('homepage'))
    else:
        return render_template('login.html')

@app.route('/homepage', methods=['GET','POST'])
def homepage():
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method =='POST':
        if request.form.get('track_search_submit') == 'Search':
            print(request.form['track_search'])
        if request.form.get('filter_search_submit') == 'Create Playlist':
            print(request.form)

    return render_template('homepage.html')

@app.route('/playlists/', methods=['GET','POST'])
def playlists():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('playlists.html', username = session['username'])

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)