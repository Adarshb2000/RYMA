from flask import Flask, render_template, request, jsonify, session, redirect
from json import dumps
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
import smtplib
import random
import ast

# To avoid recursive use of cursor
import time
import os
from threading import Lock, Timer
lock = Lock()

from helpers import apology, val, generate_otp, login_required, sample_with_exception, clear_temp

# Setting up the Database
# Students
conn = sqlite3.connect("students.db", check_same_thread=False)
db = conn.cursor()
# To take out just a particular column
with conn:
    conn.row_factory = lambda cursor, row: str(row[0])
    db_row = conn.cursor()
# Awards
conn_awards = sqlite3.connect("awards.db", check_same_thread=False)
awardsdb = conn_awards.cursor()

# Configure application
app = Flask(__name__)
app.secret_key = "ILoveYou3000"

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/awards")
def awards():
    return render_template("awards.html")

@app.route("/vote", methods=["GET", "POST"])
@login_required
def vote():
    # Getting user's info
    user_info = db.execute("SELECT * FROM y19_btech_bs WHERE id = :id", { 'id' : session.get("user_id")}).fetchall()[0]

    # Getting user's voting data
    try:
        votes = ast.literal_eval(user_info[val('votes')])
    except (ValueError, SyntaxError):
        votes = dict()

    # Getting the details of every award
    awards_info = awardsdb.execute("SELECT * FROM season_01").fetchall()

    # Dict (key, value) : (award, nominees)
    nominations = dict()

    for info in awards_info:
        # Checking if the user has already voted for a particular award
        selected_nominee = votes[info[0]] if info[0] in votes and votes[info[0]] !='' else None
        award_info = (info[0], info[1], selected_nominee)

        # Getting previous nominatoins information
        nominations_info = ast.literal_eval(info[2]) if (len(info[2]) > 0) else dict()

        # Extracting nominees and creating list
        nominees = sample_with_exception(list(nominations_info), 4, selected_nominee, 1)
        nominations[award_info] = nominees

    # Checking request method
    if request.method == "GET":
        return render_template("vote.html", nominations=nominations, selected_nominee=selected_nominee)

    for award_info in awards_info:
        add_another = True

        award_id = award_info[0]

        # Getting history
        if len(award_info[2]) > 0:
            nomination = ast.literal_eval(award_info[2])
        else:
            nomination = dict()

        # Getting user response
        nominee = request.form.get(award_id)
        print(nominee)

        # Checking if the user has already voted or not
        if award_id in votes and votes[award_id]:
            if votes[award_id] == nominee:
                continue
            elif nominee == '':
                nomination[votes[award_id]] -= 1
                add_another = False
                del votes[award_id]
            else:
                nomination[votes[award_id]] -= 1
        elif nominee == '':
            continue

        if add_another:
            votes[award_id] = nominee
            # Adding to votes
            try:
                nomination[nominee] += 1
            except KeyError:
                nomination[nominee] = 1
        
        # Saving details
        with conn_awards:
            awardsdb.execute(f"UPDATE season_01 SET nominees= :nomination WHERE award_id = '{award_id}'", {'nomination' : str(nomination)})
        
    # Saving user's data

    with conn:
        db.execute("UPDATE y19_btech_bs SET votes = :votes WHERE id = :id", { 'votes' : str(votes), 'id' : session.get("user_id") })
    
    return redirect('/home')

@app.route("/password", methods=["POST"])
def password():
    # Checking OTP verification
    if not session.get("otp_verified") or not session.get('temp_id'):
        return redirect('/register')
    # Getting user's input
    username = request.form.get('username').lower()
    password = request.form.get('password')
    confirmation = request.form.get('confirmation')

    # Validating user's input
    if not (password == confirmation):
        return "error"
    elif (password == ''):
        return "error"
    elif (username == ''):
        return "error"

    
    # Upadting database
    with conn:
        db.execute("""UPDATE 'y19_btech_bs' SET
                        rym_username = :rym_username,
                        hash = :password 
                        WHERE id= :id""",
                        {
                            'id': session.get('temp_id'),
                            'rym_username': request.form.get('username').lower(),
                            'password': request.form.get('password')
                        })
    
    # Getting user's id to create session
    info = db.execute("SELECT id FROM 'y19_btech_bs' WHERE rym_username = :rym_username", 
                        {'rym_username': request.form.get('username').lower()}).fetchall()
    session.clear()
    session["user_id"] = info[0][val('id')]
    return redirect("/home")            

@app.route("/register", methods=["GET", "POST"])
def register():
    
    # Forget any existing user
    session.clear()

    # Weather user came via a link
    if (request.method == "GET"):
        return render_template("register.html")
    else:
        # Taking user's input and error checking
        answer = str(request.form.get('answer')).lower()
        if (answer == ''):
            return "error"

        # Fetching user's data
        info = db.execute("SELECT * FROM 'y19_btech_bs' WHERE username= :username",
                            {'username': request.form.get('username').lower()}).fetchall()

        # Checking answer
        if not (len(info) == 1):
            return "error"
        
        info = info[0] 
        session["temp_id"] = info[val('id')]
        session["otp_verified"] = False
        # FOR_NOW
        """# Checking if the user had already registered
        if info[val('hash')] != '':
            return "error"

        # Getting user's email id
        email = info[val('email')]

        # Generating and sending OTP
        generate_otp(email)"""
        
        # All good
        return render_template("password.html", name=info[val('name')], username=info[val('username')])

@app.route("/log_in", methods=["GET", "POST"])
def log_in():
    # Forget any existing user
    session.clear()
    if request.method == "GET":
        return render_template("log_in.html")
    else:
        # Getting input data
        info = db.execute("""SELECT * from 'y19_btech_bs' WHERE
                            id = :answer OR
                            username = :answer OR
                            rym_username = :answer""",
                            {
                                'answer': request.form.get('answer').lower()
                            }).fetchall()

        # Error checking
        if not (len(info) == 1):
            return jsonify("false")
        info = info[0]

        # Checking weather the user has an account
        if not info[val('password')]:
            return render_template("registering.html", username=info[val('username')])

        # Checking for multiple invalid attempts
        #if not info[val('can_login')]:
            #generate_otp(info[val('email')])

        return render_template("login.html", can_login=info[val('can_login')], name=info[val('name')], username=info[val('username')], pic=info[val('pic2')], system_number=str(info[val('id')])[3 : 6])


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any existing user
    session.clear()

    # Giving log in form
    if request.method == "GET":
        return render_template("login.html")
    else:
        # Getting user's info
        info = db.execute("SELECT * FROM 'y19_btech_bs' WHERE username = :username",
                            { 'username': request.form.get('username')}).fetchall()
        if not (len(info) == 1):
            return "false"
        info = info[0]
        
        # FOR_NOW
        password = request.form.get('password')

        # Checking password
        if password != info[val('password')]:
            return "error"

        # Checking for multiple invalid attempts
        if not info[val('can_login')]:
        #    generate_otp(info[val('email')])
            return redirect('/login')
        
        # Creating session
        session["user_id"] = info[val('id')]

        # All Good
        return redirect('/home')

@app.route("/signout")
def sign_out():
    session.clear()
    return redirect('/home')

@app.route("/contact_us", methods=["GET", "POST"])
def contact_us():
    info = db.execute("SELECT * FROM y19_btech_bs where id = :roll", { "roll" : session.get("user_id")}).fetchall()
    name = info[0][val('name')] if info else None
    roll = info[0][val('id')] if info else None
    if request.method == "GET":
        return render_template("contact_us.html", name=name, id=roll)

    query = request.form.get("query")
    info = db.execute("SELECT * FROM y19_btech_bs where id = :roll", { "roll" : request.form.get("id")}).fetchall()

    person = str(info[0][val("name")]) + "(" + str(info[0][val('id')]) + ")" if info else "Someone" 
    message = person + ' says,\n\t' + query
    generate_otp("abaderia31@outlook.com", message)
    return redirect("/home")

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    roll = session.get("user_id")

    info = db.execute(f"SELECT * FROM y19_btech_bs WHERE id='{roll}'").fetchall()

    if not info:
        return redirect('/signout')
    info = info[0]

    if request.method == "GET":
        return render_template("profile.html", name=info[val('name')], username=info[val('username')], id=info[val('id')], pic=info[val('pic1')], rym_username = info[val('rym_username')])

@app.route("/username_available", methods=["GET"])
def username_available():
    # Getting user's input
    username = request.args.get("username")

    if len(username) < 4:
        return jsonify(False) 

    # Getting the list of all the usernames
    usernames = db_row.execute(f"SELECT username FROM 'y19_btech_bs'").fetchall()
    rym_username = db_row.execute(f"SELECT rym_username FROM 'y19_btech_bs'").fetchall()

    return jsonify(False) if username in usernames or username in rym_username else jsonify(True) 


@app.route("/search", methods=["GET"])
def search():
    # Getting input data
    rows = db.execute("""SELECT * from 'y19_btech_bs' WHERE name LIKE :answer OR id LIKE :answer""",
                        {
                            'answer': '%' + request.args.get('answer').lower().replace('%20', ' ') + '%'
                        }).fetchmany(5)

    info = []
    for i in range(len(rows)):
        info.append((rows[i][val('name')], rows[i][val('id')], rows[i][val('pic2')])) #FOR_NOW
    return render_template("search.html", info=info)


@app.route("/name_and_pic", methods=["GET"])
def name_and_pic():
    # Locking the cursor and the releasing it
    lock.acquire(True)
    # Getting input data
    try:
        info = db.execute("SELECT * from 'y19_btech_bs' WHERE id = :answer", { 'answer': str(request.args.get('answer')) }).fetchall()
    except sqlite3.ProgrammingError:
        return "false"
    lock.release()
    if len(info) != 1:
        return "false"
    else:
        info = info[0]
    
    
    if len(info) > 0:
        return jsonify(info[val('name')], info[val('pic2')])
    else:
        return "false"

@app.route("/login_check", methods=["GET"])
def login_check():
    # Getting input data
    info = db.execute("SELECT * from 'y19_btech_bs' WHERE id = :answer OR username = :answer OR rym_username = :answer",
                        { 'answer': request.args.get('answer').lower() }).fetchall()

    if not (len(info) == 1):
        return jsonify(False)
    register = False if info[0][val('password')] else True
    return jsonify(True, register, info[0][val('username')])

@app.route("/check", methods=["GET"])
def check():
    # Getting input data
    info = db.execute("""SELECT * from 'y19_btech_bs' WHERE id = :answer OR username = :answer""",
                        { 'answer': request.args.get('answer').lower() }).fetchall()

    # Error checking
    if not (len(info) == 1):
        return jsonify("false")
    else:
        return jsonify(info[0][val('name')], info[0][val('username')], info[0][val('pic2')])

@app.route("/password_verification", methods=["POST"])
def password_verification():

    # Getting users data
    info = db.execute("SELECT * FROM 'y19_btech_bs' WHERE username = :username",
                        { 'username': request.form.get('username') }).fetchall()
    info = info[0]


    password = request.form.get('password')

    # FOR_NOW
    return jsonify(True) if password == info[val('password')] else jsonify(False)
        


@app.route("/otp_verification", methods=["POST"])
def otp_verification():
    otp = request.form.get('otp')
    # FOR_NOW
    if (otp == session.get('my_var', None) or otp == '0000'):
        session["otp_verified"] = True
        return jsonify(True)
    else:
        return jsonify(False)
        
@app.route("/can_login", methods=["POST"])
def can_login():
    with conn:
        db.execute("UPDATE 'y19_btech_bs' SET can_login = :can_login", {'can_login': request.form.get('value')})
    return jsonify(True)

if __name__ == "__main__":
    app.run(use_reloader=True)