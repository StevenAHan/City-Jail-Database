from re import I
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

 
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
    return not (not corrPass or corrPass != password)

# Default route
@app.route("/")
def index():
    print(runStatement('''SELECT * FROM criminals'''))
    return render_template("index.html")

# Add routes here:
    
if __name__ == "__main__":
    app.run(debug=True)