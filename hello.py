from flask import Flask
from flask import Flask, redirect, render_template, request, session, url_for
import os

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return redirect(url_for('homepage'))

@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'password' and request.form['username'] == 'admin':
        session['logged_in'] = True
        return redirect(url_for('homepage'))
    else:
        return render_template('login.html')



@app.route('/homepage', methods=['GET','POST'])
def homepage():
    print(request.form['tracksearch'])
    return render_template('homepage.html')


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)