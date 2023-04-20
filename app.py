from re import I
from flask import Flask, render_template, request, Blueprint, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from flask_mysqldb import MySQL
import bcrypt
import pandas as pd

app = Flask(__name__)

login_manager = LoginManager(app)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cityjail'
 
mysql = MySQL(app)

class User:

    __hash__ = object.__hash__

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def __eq__(self, other):
        if isinstance(other, User):
            return self.get_id() == other.get_id()
        return NotImplemented

    def __ne__(self, other):
        equal = self.__eq__(other)
        if equal is NotImplemented:
            return NotImplemented
        return not equal

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Functions for obtaining db information and verifying user. Will return a dataframe of the results
def runStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df


def verifyUser(username, password):
    corrPass = runStatement('''SELECT password FROM users WHERE username=''' + username)
    user = runStatement('''SELECT password FROM users WHERE username=''' + username)
    return (corrPass and checkPassword(password, corrPass), user)


def hashPassword(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def checkPassword(password, hashed_password):
    return bcrypt.checkpw(password, hashed_password)

def addUser(username, password, security_level):
    runStatement('''INSERT INTO users VALUES(%s,%s,%s)''', username, password, security_level)

def removeAlias(criminial_id, alias):
    runStatement("DELETE FROM Aliases WHERE criminal_id=%s AND alias=%s", criminial_id, alias)

def addAlias(criminal_id, alias):
    runStatement("INSERT INTO Aliases VALUES(%s,%s)", criminal_id, alias)

# def changeCriminalName(criminal_id, newFirst, newLast):
#     runStatement(f"UPDATE Criminals SET First="{newFirst}" AND Last="{newLast}" WHERE Criminal_ID="{criminal_id}"")

# Default route
@app.route("/")
def index():
    crim = runStatement("SELECT * FROM criminals")
    return render_template("home.html", tables=[crim.to_html(classes='data')], data=crim)

# route for authenticated user
@app.route("/hi")
@login_required
def home():
    return render_template("logged_home.html")

# login page
@app.route("/login")
def login():
    return render_template("login.html")

# When user attempts login
@app.route('/login', methods=['POST'])
def login_post():
    if(request.method == "POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        if(verifyUser(username, password)[0]):
            login_user(verifyUser(username,password)[1])
            return redirect(url_for('auth.home'))
        else:
            return render_template("login.html", error="Username or Password is Incorrect, try again!")

# When searching for a criminal
@app.route("/criminals/<string:criminal_id>")
@login_required
def showCriminal(criminal_id):
    return render_template("criminal.html", data=runStatement("SELECT * FROM criminals WHERE criminal_id=" + criminal_id))

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
    
if __name__ == "__main__":
    app.run(debug=True)