from re import I
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)

 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask'
 
mysql = MySQL(app)

def insertAlias(criminal_id, alias):
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO Aliases VALUES({criminal_id},{alias}) ''')
    mysql.connection.commit()
    cursor.close()



# Default route
@app.route("/")
def index():
    return render_template("index.html")

    
if __name__ == "__main__":
    app.run(debug=True)