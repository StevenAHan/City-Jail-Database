from re import I
from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user, logout_user, LoginManager, UserMixin
from flask_mysqldb import MySQL
import bcrypt
import pandas as pd
from functools import wraps

app = Flask(__name__)
login_manager = LoginManager(app)
app.secret_key = 'my_secret_key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'cityjail'
 
mysql = MySQL(app)

class User(UserMixin):
    def __init__(self, username, power, id=None):
        self.id = id
        self.username = username
        self.power = power

    def get_power(self):
        return self.power

@login_manager.user_loader
def load_user(user_id):
    if not user_id:
        return None
    else:
        data = runStatement(f'''SELECT * FROM users WHERE username="{user_id}"''')
        user = None
        if len(data) > 0:
            user = User(username=data.iloc[0]["username"], power=data.iloc[0]["power"], id=data.iloc[0]["username"])
        return user

# if unauthorized, will automatically redirect user to login
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect("/")
        return func(*args, **kwargs)
    return decorated_view

# Functions for obtaining db information and verifying user. Will return a dataframe of the results
def runStatement(statement):
    cursor = mysql.connection.cursor()
    cursor.execute(statement)
    results = cursor.fetchall()
    mysql.connection.commit()
    df = ""
    if(cursor.description):
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(results, columns=column_names)
    cursor.close()
    return df


def hashPassword(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def checkPassword(password, hashed_password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def removeAlias(criminial_id, alias):
    runStatement(f"DELETE FROM Alias WHERE criminal_id={criminial_id} AND alias='{alias}'")

def addAlias(criminal_id, alias):
    alias_ID = runStatement(f"SELECT alias_id FROM alias")["alias_id"].max()
    print(f'INSERT INTO Alias VALUES({alias_ID + 1},{criminal_id},"{alias}")')
    runStatement(f'INSERT INTO Alias VALUES({alias_ID + 1},{criminal_id},"{alias}")')

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
    return render_template("logged_home.html", tables=[crim.to_html(classes='data')], data=crim, power=current_user.get_power())

# When user attempts login
@app.route('/', methods=['POST'])
def login_post():
    if(request.method == "POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        data = runStatement(f'''SELECT username, password, power FROM users WHERE username="{username}"''')
        if len(data) == 0:
            return render_template("login.html", error="Username or Password is Incorrect, try again!")
        elif checkPassword(password, data.iloc[0]["password"]):
            user = User(username=data.iloc[0]["username"], power=data.iloc[0]["power"], id=data.iloc[0]["username"])
            login_user(user)
            return redirect(url_for('home'))
        else:
            return render_template("login.html", error="Username or Password is Incorrect, try again!")

# When getting a criminal's information
@app.route("/criminals/<string:criminal_id>", methods=["GET", "POST"])
@login_required
def showCriminal(criminal_id):
    if request.method == "POST":
        removeAlias(criminal_id, request.form.get("dropdown"))
        return redirect("/criminals/"+criminal_id)
    return render_template("criminal.html", data=runStatement("SELECT * FROM criminals WHERE criminal_id=" + criminal_id), 
                           aliases=runStatement("SELECT * FROM Alias WHERE criminal_id=" + criminal_id),
                           crimes=runStatement("SELECT * FROM Crimes WHERE criminal_id=" + criminal_id),
                           sentences=runStatement("SELECT * FROM Sentences WHERE criminal_id=" + criminal_id),
                           power=current_user.get_power())


#Officer Information
@app.route("/officers/<string:officer_id>")
@login_required
def showOfficer(officer_id):
    return render_template("officer.html", data=runStatement("SELECT * FROM officers WHERE officer_id=" + officer_id), 
                           power=current_user.get_power())
#Appeals Information
@app.route("/appeals/<string:appeal_id>")
@login_required
def showAppeals(appeal_id):
    return render_template("appeals.html", data=runStatement("SELECT * FROM appeals WHERE appeal_id=" + appeal_id), 
                           power=current_user.get_power())

#Sentances Information
@app.route("/sentences/<string:sentence_id>")
@login_required
def showSentence(sentence_id):
    return render_template("sentences.html", data=runStatement("SELECT * FROM sentences WHERE sentence_id=" + sentence_id), 
                           power=current_user.get_power())

#Crime Information
@app.route("/crimes/<string:crime_id>")
@login_required
def showCrimes(crime_id):
    return render_template("crime.html", data=runStatement("SELECT * FROM crimes WHERE crime_id=" + crime_id),
                           appeals=runStatement("SELECT * FROM appeals WHERE crime_id=" + crime_id),
                           power=current_user.get_power())

#crimeCharge Information
@app.route("/crime_charges/<string:charge_id>")
@login_required
def showCharges(charge_id):
    data = runStatement("SELECT * FROM crime_charges WHERE charge_id=" + charge_id)
    return render_template("crimeCharge.html", data=data, 
                           code=runStatement(f"SELECT code_description FROM crime_codes JOIN crime_charges ON crime_codes.crime_code= crime_charges.crime_code WHERE crime_charges.crime_code=" + str(data.Crime_code[0])),
                           power=current_user.get_power())

#Probation Officer Information
@app.route("/prob_officer/<string:prob_id>")
@login_required
def showProbationOfficer(prob_id):
    return render_template("probationOfficer.html", data=runStatement("SELECT * FROM prob_officer WHERE prob_id=" + prob_id), 
                           sentences=runStatement("SELECT * FROM Sentences WHERE prob_id=" + prob_id),
                           power=current_user.get_power())

# to search
@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    results = []
    if request.method=="POST":
        search = request.form["search"]
        searchType = request.form["search-type"]
        searchTypeDivided = searchType.split(",")
        searchTypeDivided[1] = searchTypeDivided[1].capitalize()
        # print(searchTypeDivided[1][-2:])
        # if(searchTypeDivided[1][-2:] == "id"):
        #     searchTypeDivided[1][-2:] = "ID"
        if(searchTypeDivided[1][len(searchTypeDivided[1]) - 1] == "d"):
            if(search != ""):
                filteredResults = runStatement(f"SELECT * FROM {searchTypeDivided[0]} WHERE {searchTypeDivided[1]}={search}")
            else:
                filteredResults = runStatement(f"SELECT * FROM {searchTypeDivided[0]}")
        else:
            filteredResults = runStatement(f"SELECT * FROM {searchTypeDivided[0]} WHERE {searchTypeDivided[1]} LIKE '{search}%'")

        for index, filteredResult in filteredResults.iterrows():
            print(filteredResult)
            if(searchTypeDivided[1][len(searchTypeDivided[1]) - 1] == "d"):
                results.append(f"<a href=/{str(searchTypeDivided[0])}/{str(filteredResult[0])}>" + str(filteredResult[0])
                           + "<a>" + "<br>")
            else:
                results.append(f"<a href=/{searchTypeDivided[0]}/{filteredResult[0]}>" + filteredResult[searchTypeDivided[1]]
                           + "<a>" + "<br>")
        results = " ".join(results)
    return render_template("search.html", results=results, searchType=searchTypeDivided[0])

#to logout
@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
    

@app.route("/criminals/<string:criminal_id>/removealias/<string:alias>")
@login_required
def deleteAlias(criminal_id, alias):
    if current_user.get_power() == "V":
        return redirect("/")
    removeAlias(criminal_id, alias)
    return redirect(f"/criminal/{criminal_id}")

@app.route("/criminals/<string:id>/editfirst/", methods=["GET", "POST"])
@login_required
def changeCrimFirstPage(id):
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        newFirst = request.form.get('first')
        print(newFirst)
        runStatement(f"UPDATE criminals SET First='{newFirst}' WHERE criminal_id='{id}'")
        return redirect(f"/criminals/{id}")
    return render_template("criminal_change_first.html", id=id)

@app.route("/officers/<string:id>/editfirst/", methods=["GET", "POST"])
@login_required
def changeOfficerFirstPage(id):
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        newFirst = request.form.get('first')
        runStatement(f"UPDATE officers SET First='{newFirst}' WHERE officer_id='{id}'")
        return redirect(f"/officers/{id}")
    return render_template("officer_change_first.html", id=id)

@app.route("/prob_officer/<string:id>/editfirst/", methods=["GET", "POST"])
@login_required
def changeProbOfficerFirstPage(id):
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        newFirst = request.form.get('first')
        runStatement(f"UPDATE prob_officer SET First='{newFirst}' WHERE prob_id='{id}'")
        return redirect(f"/prob_officer/{id}")
    return render_template("prob_officer_change_first.html", id=id)


@app.route("/criminals/<string:criminal_id>/addalias", methods=["GET", "POST"])
@login_required
def addAliasPage(criminal_id):
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        newAlias = request.form.get('alias')
        addAlias(criminal_id, newAlias)
        return redirect(f"/criminals/{criminal_id}")
    return render_template("add_alias.html", criminal_id=criminal_id)


@app.route("/payfine/<string:charge_id>", methods=["GET", "POST"])
@login_required
def payFine(charge_id):
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        runStatement(f"CALL pay_fines({request.form.get('payment')}, {charge_id});")
        return redirect(f"/crime_charges/{charge_id}")
    return render_template("pay_fine.html", id=charge_id)

@app.route("/crimes/add", methods=["GET", "POST"])
@login_required
def addCrime():
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        crime_id = runStatement(f"SELECT crime_id FROM crimes")["crime_id"].max() + 1
        crimID = request.form.get('criminal_ID')
        classification = request.form.get('classification')
        date_charged = request.form.get('date_charged')
        status = request.form.get('status')
        hearing_date = request.form.get('hearing_date') 
        runStatement(f'''INSERT INTO Crimes (Crime_ID,Criminal_ID,Classification,Date_charged,Status,Hearing_date) 
                     VALUES({crime_id},{crimID},'{classification}','{date_charged}',"{status}",'{hearing_date}');''')
        return redirect(f"/home")
    return render_template("add_crime.html")

@app.route("/criminals/add", methods=["GET", "POST"])
@login_required
def addCriminal():
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        crim_id = runStatement(f"SELECT criminal_id FROM criminals")["criminal_id"].max() + 1
        first = request.form.get('first')
        last = request.form.get('last')
        addr = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state') 
        zip = request.form.get('zip') 
        phone = request.form.get('phone') 
        vstat = request.form.get('vstat') 
        pstat = request.form.get('pstat') 
        runStatement(f'''INSERT INTO Criminals VALUES({crim_id},"{last}","{first}","{addr}","{city}","{state}","{zip}","{phone}","{vstat}","{pstat}");''')
        return redirect(f"/home")
    return render_template("add_criminal.html")

@app.route("/officers/add", methods=["GET", "POST"])
@login_required
def addOfficer():
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        officer_id = runStatement(f"SELECT officer_id FROM officers")["officer_id"].max() + 1
        first = request.form.get('first')
        last = request.form.get('last')
        precinct = request.form.get('precinct')
        badge = request.form.get('badge')
        phone = request.form.get('phone')
        status = request.form.get('status')
        runStatement(f'''INSERT INTO Officers VALUES({officer_id},"{last}","{first}","{precinct}",{badge}","{phone}","{status}");''')
        return redirect(f"/home")
    return render_template("add_officer.html")

@app.route("/prob_officer/add", methods=["GET", "POST"])
@login_required
def addProbOfficer():
    if current_user.get_power() == "V":
        return redirect("/")
    if request.method == "POST":
        prob_id = runStatement(f"SELECT prob_id FROM prob_officer")["prob_id"].max() + 1
        first = request.form.get('first')
        last = request.form.get('last')
        addr = request.form.get('address')
        city = request.form.get('city')
        state = request.form.get('state') 
        zip = request.form.get('zip') 
        phone = request.form.get('phone') 
        email = request.form.get("email")
        status = request.form.get("status")
        runStatement(f'''INSERT INTO Prob_officer VALUES({prob_id},"{last}","{first}","{addr}","{city}","{state}","{zip}","{phone}","{email}","{status}");''')
        return redirect(f"/home")
    return render_template("add_prob_officer.html")


@app.route("/prob_officer/delete/<string:prob_id>")
@login_required
def deleteProbOfficer(prob_id):
    if current_user.get_power() == "V":
        return redirect("/")
    runStatement(f'''DELETE FROM prob_officer WHERE prob_id={prob_id};''')
    return redirect("/home")

@app.route("/officers/delete/<string:id>")
@login_required
def deleteOfficer(id):
    if current_user.get_power() == "V":
        return redirect("/")
    runStatement(f'''DELETE FROM officers WHERE officer_id={id};''')
    return redirect("/home")

@app.route("/criminals/delete/<string:id>")
@login_required
def deleteCriminal(id):
    if current_user.get_power() == "V":
        return redirect("/")
    runStatement(f'''DELETE FROM criminals WHERE criminal_id={id};''')
    return redirect("/home")

@app.route("/crimes/delete/<string:id>")
@login_required
def deleteCrime(id):
    if current_user.get_power() == "V":
        return redirect("/")
    runStatement(f'''DELETE FROM crimes WHERE crime_id={id};''')
    return redirect("/home")

if __name__ == "__main__":
    app.run(debug=True)
