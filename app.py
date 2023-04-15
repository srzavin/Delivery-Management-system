from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from datetime import date


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#initializing database
db = SQLAlchemy(app)


class UserInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(200), nullable = False)
    password = db.Column(db.String(200), nullable = False)
    role = db.Column(db.String(200), nullable=False)


    def __init__(self,name,email, password,role):
        self.name = name
        self.email = email
        self.password = password
        self.role = role


class ParcelInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pname = db.Column(db.String(200), nullable = False)
    pemail = db.Column(db.String(200), nullable = False)
    pLocP = db.Column(db.String(200), nullable = False)
    dLocP = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pStat = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Integer, nullable = False)
    paystat = db.Column(db.Integer, nullable=False)
    createdBy = db.Column(db.String(200), nullable=False)


    def __init__(self,pname,pemail, pLocP,dLocP,date,pStat, amount,paystat, createdBy):
        self.pname = pname
        self.pemail = pemail
        self.pLocP = pLocP
        self.dLocP = dLocP
        self.date = date
        self.pStat = pStat
        self.amount = amount
        self.paystat = paystat
        self.createdBy = createdBy

app.secret_key = "password"
app.static_folder = 'static'
with app.app_context():
    db.create_all()

@app.route('/', methods=["POST","GET"])
def login():  # put application's code here
    if request.method == "POST":
        email_addr = request.form["email"]
        pass_login = request.form['pass']
        session["Email"] = email_addr

        chckuser = UserInfo.query.filter_by(email = email_addr ).first()
        if chckuser and chckuser.password == pass_login:
            if chckuser.role == 'merchant':
                session['Email'] = chckuser.email
                return redirect(url_for("merchant"))
            else:
                session['Email'] = chckuser.email
                return redirect(url_for("user"))

        else:
            flash("USER NOT FOUND","error")
            return render_template("login/index.html")
    else:
        return render_template("login/index.html")

@app.route('/new_user', methods=["POST","GET"])
def new_user():  # put application's code here
    if request.method == "POST":
        name_form = request.form['name']
        email_form = request.form['email']
        password_form = request.form['pass']
        role_form = request.form['roles']

        info = UserInfo(name_form,email_form,password_form,role_form)

        db.session.add(info)
        db.session.commit()
        flash("User Added")
        return redirect(url_for("login"))
    else:
        return render_template("create_user.html")

@app.route('/user')
def user():  # put application's code here
    if "Email" in session:
        email = session["Email"]
        chckuser = UserInfo.query.filter_by(email=email).first()
        name = chckuser.name
        info = ParcelInfo.query.filter_by(pemail=email, pStat="Dispatched")
        return render_template('user.html', name = name, queer = info)
    else:
        return redirect(url_for("login"))

@app.route('/merchant', methods= ["POST","GET"])
def merchant():  # put application's code here

    if "Email" in session:
        email = session["Email"]
        chckuser = UserInfo.query.filter_by(email=email).first()
        name = chckuser.name
        info = ParcelInfo.query.filter_by(createdBy = email ,pStat="Dispatched")
        if request.method == "POST":
            pId  = request.form['id']
            rec = ParcelInfo.query.filter_by(id = pId).first()
            rec.pStat = "Received"
            db.session.commit()

        return render_template('merchant.html', name = name, queer = info)
    else:
        return redirect(url_for("login"))


@app.route('/parceladd', methods = ["POST","GET"])
def parceladd():  # put application's code here
    email = session["Email"]
    if request.method == "POST":
        pemail_form = request.form['mpemail']
        pName_form = request.form['pName']
        sLocp_form = request.form['sLoc']
        dLocp_form = request.form['dLoc']
        date_form = request.form['date']
        amount_form = request.form['famount']
        date_ob = date.fromisoformat(date_form)
        stat = 'Dispatched'
        pays = 0
        createE = email


        parcelInfo =  ParcelInfo(pName_form,pemail_form, sLocp_form,dLocp_form,date_ob,stat,amount_form,pays,createE)

        db.session.add(parcelInfo)
        db.session.commit()
        flash("Parcel Added")
        return redirect(url_for("parceladd"))
    else:
        return render_template('parceladd.html')




@app.route('/parcels')
def parcelH():  # put application's code here
    email = session["Email"]
    items = ParcelInfo.query.filter_by(createdBy = email)

    return render_template('parcels.html', queer = items)





@app.route('/userParcels')
def parcelU():  # put application's code here

    email = session["Email"]
    chckuser = ParcelInfo.query.filter_by(pemail=email)

    return render_template('userParcels.html', queer = chckuser)






@app.route('/payportal', methods =["POST", "GET"])
def payget():  # put application's code here
    pid = request.args.get('id')
    print(pid)
    if request.method == "POST":
        record = ParcelInfo.query.filter_by(id=pid).first()
        record.paystat = 1
        db.session.commit()

        return redirect(url_for("payment"))
    else:
        return render_template('payment_portal.html')





@app.route('/payment', methods = ["POST","GET"])
def payment():  # put application's code here

    email = session["Email"]
    info  = ParcelInfo.query.filter_by(pemail=email, paystat = 0 )
    if request.method == "POST":
        pId = request.form['id']


        return redirect(url_for('payget', id=pId))
    else:
        return render_template('payment.html', queer = info)































@app.route('/logout')
def logout():  # put application's code here
    session.pop("Email", None)
    return redirect(url_for("login"))




if __name__ == '__main__':


    app.run(debug=True)