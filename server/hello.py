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
        session['filter_list'] = []
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
            filter_list = []
            for key in ['artist_name', 'album_name']:
                filter_list.append(request.form[key])
            for key in ['track_pop_lowerbound', 'track_pop_upperbound', \
                'duration_lowerbound', 'duration_upperbound', \
                'vocal_rate_lowerbound', 'vocal_rate_upperbound',\
                'danceable_rate_lowerbound', 'danceable_rate_upperbound',\
                'tempo_lowerbound', 'tempo_upperbound', 'key']:
                if isfloat(request.form[key]) != 'error':
                    filter_list.append(isfloat(request.form[key]))
                else:
                    query = text("select p.playlist_id, p.name from Playlist_Produce as p where p.email = :email")
                    cursor = conn.execute(query, email=session['email'])
                    playlist = list(cursor.fetchall())
                    return render_template('homepage.html', \
                        url=request.host_url+'playlists/', playlist=playlist, \
                        message="Value error, please try again. ")
            
            session['filter_list'] = filter_list
            return redirect(url_for('create_playlist'))
    
    query = text("select p.playlist_id, p.name from Playlist_Produce as p where p.email = :email")
    cursor = conn.execute(query, email=session['email'])
    playlist = list(cursor.fetchall())
    return render_template('homepage.html', \
        url=request.host_url+'playlists/', playlist=playlist, message="")

def isfloat(e):
    if not e:
        return e
    try:
        return float(e)
    except ValueError:
        return 'error'

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
        if request.form.get('comment_content') == 'Comment':
            comment_text = request.form['comment_text']
            query3 = text('''SELECT Count(*) FROM Comment''')
            cursor3 = conn.execute(query3)
            commen_id = cursor3.fetchall()
            comment_id =5030 + commen_id[0][0]
            query = text('''INSERT INTO Comment VALUES (:comment_id, :track_id, :email, :content)''')
            cursor =conn.execute(query,comment_id = comment_id,track_id = track_id,email =session['email'],content = comment_text)
            query = text('''SELECT Track.track_name,Album.album_name,Artist.artist_name,Track.track_pop,Track.duration,
    Track.vocal_rate,Track.danceable_rate,Track.tempo,Track.key FROM Track,Album,Track_in_album,Artist,Create_track 
    WHERE Track.track_id = :id and Track.track_id =Track_in_album.track_id and Track_in_album.album_id = Album.album_id and
    Track.track_id = Create_track.track_id and Artist.artist_id = Create_track.artist_id''')
            query2 = text('''SELECT Comment.content,Comment.email FROM Comment WHERE Comment.track_id = :track_id ''')
            cursor2 = conn.execute(query2,track_id =track_id)
            cursor = conn.execute(query,id = track_id)
            comment = list(cursor2.fetchall())
            sum = list(cursor.fetchall())
            return render_template('songpage.html', songname = sum, comment = comment)
        if request.form.get('back_home_page') == 'Back':
            return redirect(url_for('homepage'))

    query = text('''SELECT Track.track_name,Album.album_name,Artist.artist_name,Track.track_pop,Track.duration,
    Track.vocal_rate,Track.danceable_rate,Track.tempo,Track.key FROM Track,Album,Track_in_album,Artist,Create_track 
    WHERE Track.track_id = :id and Track.track_id =Track_in_album.track_id and Track_in_album.album_id = Album.album_id and
    Track.track_id = Create_track.track_id and Artist.artist_id = Create_track.artist_id''')
    cursor = conn.execute(query,id = track_id)
    sum = list(cursor.fetchall())
    query2 = text('''SELECT Comment.content,Comment.email FROM Comment WHERE Comment.track_id = :track_id ''')
    cursor2 = conn.execute(query2,track_id =track_id)
    comment = list(cursor2.fetchall())
    return render_template('songpage.html', songname = sum,comment = comment)

@app.route('/playlists/<int:playlist_id>', methods=['GET','POST'])
def playlists(playlist_id):
    if not session.get('logged_in'):
        return render_template('login.html')
    if 'back_button' in request.form:
        return redirect(url_for('homepage'))
    query = text('''SELECT Track.track_id, Track.track_name FROM TRACK WHERE Track.track_id in 
(SELECT Track_has_playlist.track_id FROM Track_has_playlist WHERE Track_has_playlist.playlist_id = :id)''')
    cursor = conn.execute(query,id = playlist_id)
    songs = list(cursor.fetchall())
    return render_template('playlists.html', songs = songs, url=request.host_url+'songpage/')

@app.route('/create_playlist', methods=['GET','POST'])
def create_playlist():
    if not session.get('logged_in'):
        return render_template('login.html')
    if request.method =='POST':
        if 'back_button' in request.form:
            session['create_playlist'] = None
            return redirect(url_for('homepage'))
        if 'save_button' in request.form:
            #insert plsylist_Produce
            if len(session['create_playlist'])<1:
                return redirect(url_for('homepage'))
            query2 = text('''SELECT Count(*) FROM Track_has_playlist''')
            cursor2 = conn.execute(query2)
            new_name_id = cursor2.fetchall()
            new_name_id =1 + new_name_id[0][0]
            name = 'mylove' + str(new_name_id)

            query = text('''SELECT Count(*) FROM Track_has_playlist''')
            cursor = conn.execute(query)
            new_playlist_id = cursor.fetchall()
            new_playlist_id =4001 + new_playlist_id[0][0]
            track_id = session['create_playlist'][0]

            query3 = text('''INSERT INTO Playlist_Produce VALUES (:playlist_id, :email, :name)''')
            cursor3 =conn.execute(query3,playlist_id = new_playlist_id,email = session['email'], name = name)


            for track_id in session['create_playlist']:
                query1 = text('''INSERT INTO Track_has_playlist VALUES (:track_id, :playlist_id)''')
                cursor1 =conn.execute(query1,track_id = track_id,playlist_id = new_playlist_id)

            #back homepage
            return redirect(url_for('homepage'))


    if request.method =='GET':
        filter_list = session['filter_list']
        restrictions = []
        artist_name = filter_list[0]
        if artist_name != '':
            artist_name = '%' + artist_name + '%'
            restrictions.append('t.track_id=tart.track_id and tart.artist_id=art.artist_id and art.artist_name ilike :artist_name')
        album_name = filter_list[1]
        if album_name != '':
            album_name = '%' + album_name + '%'
            restrictions.append('t.track_id=talb.track_id and talb.album_id=alb.album_id and alb.album_name ilike :album_name')
        track_pop_lowerbound = filter_list[2]
        if track_pop_lowerbound != '':
            restrictions.append('t.track_pop >= :track_pop_lowerbound')
        track_pop_upperbound = filter_list[3]
        if track_pop_upperbound != '':
            restrictions.append('t.track_pop <= :track_pop_upperbound')
        duration_lowerbound = filter_list[4]
        if duration_lowerbound != '':
            restrictions.append('t.duration >= :duration_lowerbound')
        duration_upperbound = filter_list[5]
        if duration_upperbound != '':
            restrictions.append('t.duration <= :duration_upperbound')
        vocal_rate_lowerbound = filter_list[6]
        if vocal_rate_lowerbound != '':
            restrictions.append('t.vocal_rate >= :vocal_rate_lowerbound')
        vocal_rate_upperbound = filter_list[7]
        if vocal_rate_upperbound != '':
            restrictions.append('t.vocal_rate <= :vocal_rate_upperbound')
        danceable_rate_lowerbound = filter_list[8]
        if danceable_rate_lowerbound != '':
            restrictions.append('t.danceable_rate >= :danceable_rate_lowerbound')
        danceable_rate_upperbound = filter_list[9]
        if danceable_rate_upperbound != '':
            restrictions.append('t.danceable_rate <= :danceable_rate_upperbound')
        tempo_lowerbound = filter_list[10]
        if tempo_lowerbound != '':
            restrictions.append('t.tempo >= :tempo_lowerbound' ) 
        tempo_upperbound = filter_list[11]
        if tempo_upperbound != '':
            restrictions.append('t.tempo <= :tempo_upperbound' ) 
        key = filter_list[12]
        if key != '':
            restrictions.append('t.key = :key')
        sqltext = '''SELECT distinct t.track_id, t.track_name FROM Track as t, Create_track as tart, Track_in_album as talb, Album as alb, Artist as art'''
        if restrictions:
            postfix = ' and '.join(restrictions)
            sqltext = sqltext + " WHERE " + postfix
        query = text(sqltext)
        cursor = conn.execute(query, artist_name=artist_name, album_name=album_name, \
            track_pop_lowerbound=track_pop_lowerbound, track_pop_upperbound=track_pop_upperbound, \
            duration_lowerbound=duration_lowerbound, duration_upperbound=duration_upperbound, \
            vocal_rate_lowerbound=vocal_rate_lowerbound, vocal_rate_upperbound=vocal_rate_upperbound, \
            danceable_rate_lowerbound=danceable_rate_lowerbound, danceable_rate_upperbound=danceable_rate_upperbound, \
            tempo_lowerbound=tempo_lowerbound, tempo_upperbound=tempo_upperbound, key=key)
        songs = list(cursor.fetchall())
        session['create_playlist'] = []
        for i in range(len(songs)):
            session['create_playlist'].append(songs[i][0])

        return render_template('create_playlist.html', url=request.host_url+'songpage/', \
            result_songs=songs)



if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=8111)