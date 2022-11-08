from flask import Flask, redirect, render_template, request, session, url_for
import os
from sqlalchemy import *
from sqlalchemy.sql import text

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

@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        query = text("select * from User_info as u where u.email = :email and u.password = :password")
        cursor = conn.execute(query, email=email, password=password)
        account_info = cursor.fetchone()
        if not account_info:
            return render_template('login.html')
        session['logged_in'] = True
        session['email'] = account_info[0]
        session['password'] = account_info[1]
        return redirect(url_for('homepage'))
    
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
    
    email = session['email']
    query = text("select p.playlist_id, p.name from Playlist_Produce as p where p.email = :email")
    cursor = conn.execute(query, email=email)
    playlist = list(cursor.fetchall())
    return render_template('homepage.html')

@app.route('/playlists/', methods=['GET','POST'])
def playlists():
    if not session.get('logged_in'):
        return render_template('login.html')
    return render_template('playlists.html', email = session['email'])

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)