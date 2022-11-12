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
            return render_template('login.html', message="Wrong Email or password!")
        session['logged_in'] = True
        session['email'] = account_info[0]
        session['password'] = account_info[1]
        return redirect(url_for('homepage'))
    
    return render_template('login.html', message="")

@app.route('/homepage', methods=['GET','POST'])
def homepage():
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method =='POST':

        if request.form.get('track_search_submit') == 'Search':
            search_word = request.form['track_search']
            return redirect(url_for('search_result', search_word=search_word))

        if request.form.get('filter_search_submit') == 'Create Playlist':
            print(request.form)#TODO
    
    query = text("select p.playlist_id, p.name from Playlist_Produce as p where p.email = :email")
    cursor = conn.execute(query, email=session['email'])
    playlist = list(cursor.fetchall())
    return render_template('homepage.html', \
        url=request.host_url+'playlists/', playlist=playlist)

@app.route('/search_result/<search_word>', methods=['GET','POST'])
def search_result(search_word):
    if not session.get('logged_in'):
        return render_template('login.html')
    search_word_sql = '%' + search_word + '%'
    query = text("select * from Track as t where t.track_name ilike :search_word_sql")
    cursor = conn.execute(query, search_word_sql=search_word_sql)
    result_songs = list(cursor.fetchall())
    return render_template('search_result.html', search_word=search_word, \
        url=request.host_url+'songpage/', result_songs=result_songs)

@app.route('/songpage/<int:track_id>', methods=['GET','POST'])
def songpage(track_id):
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method =='POST':
        print("11111")
        if request.form.get('comment_content') == 'Comment':
            comment_text = request.form['comment_text']
            print(comment_text)

        if request.form.get('back_home_page') == 'Back':
            return redirect(url_for('homepage'))

    query = text('''SELECT Track.track_name,Album.album_name,Artist.artist_name,Track.track_pop,Track.duration,
    Track.vocal_rate,Track.danceable_rate,Track.tempo,Track.key FROM Track,Album,Track_in_album,Artist,Create_track 
    WHERE Track.track_id = :id and Track.track_id =Track_in_album.track_id and Track_in_album.album_id = Album.album_id and
    Track.track_id = Create_track.track_id and Artist.artist_id = Create_track.artist_id''')
    cursor = conn.execute(query,id = track_id)
    sum = list(cursor.fetchall())
    return render_template('songpage.html', songname = sum)

@app.route('/playlists/<int:playlist_id>', methods=['GET','POST'])
def playlists(playlist_id):
    if not session.get('logged_in'):
        return render_template('login.html')

    query = text('''SELECT Track.track_name FROM TRACK WHERE Track.track_id in 
(SELECT Track_has_playlist.track_id FROM Track_has_playlist WHERE Track_has_playlist.playlist_id = :id)''')
    cursor = conn.execute(query,id = playlist_id)
    sum = list(cursor.fetchall())
    
    return render_template('playlists.html', song = sum)


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)