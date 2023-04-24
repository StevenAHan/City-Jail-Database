from re import I
from flask import Flask, render_template, request, Blueprint, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user, LoginManager
from flask_mysqldb import MySQL
import bcrypt
import pandas as pd

app = Flask(__name__)
# hello
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
    data = runStatement(f'''SELECT username, password FROM users WHERE username="{username}"''')
    corrPass = data.iloc[0]["password"]
    user = data.iloc[0]["username"]
    return (corrPass and checkPassword(password, hashPassword(corrPass)), user)


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

def changeCriminalName(criminal_id, newFirst, newLast):
    runStatement(f'UPDATE Criminals SET First="{newFirst}" AND Last="{newLast}" WHERE Criminal_ID="{criminal_id}"')

# Default route
@app.route("/")
def index():
    return render_template("login.html")

@app.route("/home")
@login_required
def home():
    crim = runStatement("SELECT * FROM criminals")
    print(crim)
    return render_template("logged_home.html", tables=[crim.to_html(classes='data')], data=crim)

# When user attempts login
@app.route('/', methods=['POST'])
def login_post():
    if(request.method == "POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        if(verifyUser(username, password)[0]):
            login_user(verifyUser(username,password)[1])
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Username or Password is Incorrect, try again!")

# When searching for a criminal
@app.route("/criminals/<string:criminal_id>")
@login_required
def showCriminal(criminal_id):
    print(runStatement("SELECT * FROM Alias WHERE criminal_id=" + criminal_id))
    return render_template("criminal.html", data=runStatement("SELECT * FROM criminals WHERE criminal_id=" + criminal_id), 
                           aliases=runStatement("SELECT * FROM Alias WHERE criminal_id=" + criminal_id))

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    if request.method=="POST":
        search = request.form["search"]
        searchType = request.form["search-type"]
        searchTypeDivided = searchType.split(",")
        searchTypeDivided[1] = searchTypeDivided[1].capitalize()
        filteredResults = runStatement(f"SELECT * FROM {searchTypeDivided[0]} WHERE {searchTypeDivided[1]} LIKE '{search}%'")

        for index, filteredResult in filteredResults.iterrows():
            print(filteredResult)
            results.append(f"<a href=/{searchTypeDivided[0]}/{filteredResult[0]}>" + filteredResult[searchTypeDivided[1]] 
                           + "<a>" + "<br>")
        results = " ".join(results)
        print(results)
    return render_template("search.html", results=results)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

    
if __name__ == "__main__":
    app.run(debug=True)