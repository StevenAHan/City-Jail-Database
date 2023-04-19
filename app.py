from re import I
from flask import Flask, render_template, request, Blueprint
from flask_login import login_user, login_required, current_user
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

norm = Blueprint('norm', __name__)

auth = Blueprint("auth", __name__)
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cityjail'
 
mysql = MySQL(app)

def runStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    mysql.connection.commit()
    cursor.close()
    return results


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


# Default route
@norm.route("/")
def index():
    print(runStatement('''SELECT * FROM criminals'''))
    return render_template("index.html")

# Add routes here:
@auth.route("/")
@login_required
def home():
    return render_template("logged_home.html")

@norm.route("/login")
def login():
    return render_template("login.html")

@norm.route('/login', methods=['POST'])
def login_post():
    if(method == "POST"):
        if(verifyUser())
    return redirect(url_for('main.profile'))
    
if __name__ == "__main__":
    app.run(debug=True)