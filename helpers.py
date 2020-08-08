from flask import redirect, render_template, request, session
import smtplib
import random
from functools import wraps

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/log_in")
        return f(*args, **kwargs)
    return decorated_function

def generate_otp(email, message = None):
    if not message:
        # Generating OTP & storing it's value and message
        OTP = str(random.randint(1000, 9999))
        session['my_var'] = f"{OTP}"
        message = "Your OTP for Rate Your Mate! is " + OTP + "."

    # Sending Email
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login("rymaIITK@gmail.com", "a!1234IIT")
    server.sendmail("rymaIITK@gmail.com", email, message)

def val(argument):
    switcher = {
        'id': 0,
        'roll': 0,
        'name': 1,
        'username': 2,
        'email': 3,
        'rym_username': 4,
        'hash': 5,
        'password': 5,
        'pic1': 6,
        'pic2': 7,
        'pic3': 8,
        'can_login': 9,
        'votes': 10
    }

    return switcher.get(argument, None)

def sample_with_exception(population, k, elem = None, position = None):
    # Checking k
    k = len(population) if (k > len(population)) else k

    # Checking element
    if elem:
        population.remove(elem)
        k -= 1
        new_population = random.sample(population, k)
        new_population.insert(position - 1, elem) if position else new_population.insert(random.randint(0, k), elem)
        return new_population
    else:
        return random.sample(population, k)


def clear_temp():
    session.pop('temp_id')