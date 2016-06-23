from flask import Flask,render_template,redirect,url_for,request,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///User_Login.sqlite3'
app.config["SQLALCHEMY_BINDS"]={'login': 'sqlite:///User_Login.sqlite3','info': 'sqlite:///User_info.sqlite3'}

app.config["SECRET_KEY"]='Jeevesh'
db=SQLAlchemy(app)
class User_Login(db.Model):
    __tablename__='User_Login'
    __bind_key__='login'
    id = db.Column(db.Integer,primary_key=True)
    name= db.Column(db.String(100))
    username= db.Column(db.String(100))
    password= db.Column(db.String(20))
    number= db.Column(db.Integer)

    def __init__(self,name,username,password,number):
        self.name=name
        self.username=username
        self.password=password
        self.number=number
@app.route('/')
def login():
    db.session.add(User_Login('Admin','admin','admin',1234))
    db.session.commit()
    return render_template('login.html')
@app.route('/signup')
def signup():
    return render_template('sign-up.html')
@app.route('/logged_in',methods=['POST','GET'])
def logged_in():
    if request.method == 'POST':
        user=User_Login.query.filter_by(username=request.form['user']).first()
        if not User_Login.query.filter_by(username=request.form['user']).count():
            flash('Please Sign Up First')
            return redirect(url_for('login'))
        elif user.password != request.form['password']:
            flash('Please enter the correct details')
            return redirect(url_for('login'))
        else:
            return render_template('Info.html')
@app.route('/signed_up',methods=['POST','GET'])
def signed_up():
    if request.method == 'POST':
        if not request.form['name'] or not request.form['user'] or not request.form['password'] or not request.form['rep_password']:
            flash("Fill All The Fields ")
        elif request.form['password'] != request.form['rep_password']:
            flash("Passwords Don't Match")
        elif User_Login.query.filter_by(username=request.form['user']).count():
            flash("Please choose a different Username")
        elif User_Login.query.filter_by(name=request.form['name'],number=request.form['number']).count():
            flash("User already registered")
        else:
            user=User_Login(request.form["name"],request.form["user"],request.form["password"],request.form["number"],)
            db.session.add(user)
            db.session.commit()
            return render_template('Info.html',users=User_Login.query.all())
            #render_template('Info.html',user=User_Login.query.filter_by(username=request.form['user']).first())
    return redirect(url_for('signup'))
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
