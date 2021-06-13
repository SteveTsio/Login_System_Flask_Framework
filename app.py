from os import environ
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
import sqlite3
from inspect import cleandoc #μπορέι να μήν χρειαστεί
from pathlib import Path
#importing ολα όσα θα χρειαστώ

app = Flask(__name__)

#Μεταβλητή για το path της DB
DATABASE_PATH = Path(__file__).parent / 'data/system.db'

#Τo secret key είναι σε άλλο mmodule για ασφάλεια
app.secret_key = environ.get('SECRET_KEY', 'dhfiu483irnfeiooe')

def get_conn():
    if 'conn' not in g:
        app.logger.debug(f"» New Connection requested from endpoint '{request.endpoint}'")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        g.conn = conn

    return g.conn

#Ανοιγμα του connection πρίν το request
@app.before_request
def connection():
    conn = sqlite3.connect(DATABASE_PATH)
    g.conn = conn

#Καταστροφή του connection μετά το request
@app.teardown_appcontext
def close_connection(ctx):
    '''
    Close connection on appcontext teardown
    This will fire whether there was an exception or not
    '''
    if conn := g.pop('conn', None):
        app.logger.debug('» Connection closed')
        conn.close()



#main page Το πρώτο view θα αφορά στην “αρχική σελίδα” (route “/”) Αναφέρεται στην εργασία ώς πρώτο route
@app.get('/')
def index():
    return render_template('index.html')

#Εδώ είναι η error σελίδα διαχείρισης λαθών
@app.get('/error')
def error():
    return render_template('error.html')

#Εδώ είναι η σελίδα που περιέχει την φόρμα με το login Αναφέρεται στην εργασία ώς δεύτερο route
@app.get('/login')
def form():
    return render_template('login.html')

#Εδώ είναι η λειτουργικότητα της φόρμας με το login
@app.post('/login')
def login():
    password = request.form["password"]
    username = request.form["username"]

    cur = get_conn().cursor()
    user = cur.execute(
        '''
        SELECT [username], [password]
        FROM [users]
        WHERE [username] = :username AND [password] = :password
        ''', {'username': username, 'password' :password }
    ).fetchone()

    setattr(g, 'user', user)

    cur.close()

    if not user:
        flash('Please try again')
        errors = True
        return redirect(url_for('login'))
    else:
        password = request.form["password"]
        username = request.form["username"]

        session["username"] = username
        session['logged_in'] = True
        return render_template('profile.html', username = username)


#Εδώ είναι η σελίδα που φέρνει το προφίλ του χρήστη  Αναφέρεται στην εργασία ώς τρίτο route
@app.route('/profile/<username>')
def profile(username):
    if session.get('username') is None:
        return render_template('login.html')
    elif session["username"] == username:
        cur = get_conn().cursor()
        mail = cur.execute(
        '''
        SELECT [email]
        FROM [users]
        WHERE [username] = :username
        ''', {'username': username }
        ).fetchone()

        setattr(g, 'mail', mail)

        cur.close()

        return render_template('profile.html', username = username, mail = mail)
    else:
        abort(401)


#Εδώ είναι η λειτουργικότητα logout οπου κάνει pop τα στοιχεία απο το session Αναφέρεται στην εργασία ώς τελευταίο view
@app.get('/logout')
def logout():
    session.pop("loged_in", None)
    session.pop("username", None)
    session.pop("password", None)
    flash('You logged out')
    return redirect(url_for('login'))
