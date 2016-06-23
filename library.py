from flask import Flask,render_template,redirect,url_for,request,flash
from flask.ext.mongoalchemy import MongoAlchemy

app=Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///User_Login.sqlite3'
app.config['MONGOALCHEMY_DATABASE'] = 'login'
app.config['SECRET_KEY']='Je123'

db1=MongoAlchemy(app)
class User_Login(db1.Document):
    name= db1.StringField()
    username= db1.StringField()
    password= db1.StringField()
    number= db1.IntField()

@app.route('/')
def login():
    return render_template('login.html')
@app.route('/signup')
def signup():
    return render_template('sign-up.html')
@app.route('/logged_in',methods=['POST','GET'])
def logged_in():
    if request.method == 'POST':
        user=User_Login.query.filter(User_Login.username==request.form['user']).first()
        if not user:
            flash('Please Sign Up First')
            return redirect(url_for('login'))
        elif user.password != request.form['password']:
            flash('Please enter the correct details')
            return redirect(url_for('login'))
        else:
            return "Login Successfull"
@app.route('/signed_up',methods=['POST','GET'])
def signed_up():
    if request.method == 'POST':
        newuser=User_Login(name=request.form["name"],username=request.form["user"],password=request.form["password"],number=long(request.form["number"]))
        if not request.form['name'] or not request.form['user'] or not request.form['password'] or not request.form['rep_password']:
            flash("Fill All The Fields ")
        elif request.form['password'] != request.form['rep_password']:
            flash("Passwords Don't Match")
        elif User_Login.query.filter(User_Login.name==request.form['name']).first() or User_Login.query.filter(User_Login.number==long((request.form['number']))).first():
            flash("User already registered")
        elif User_Login.query.filter(User_Login.username==request.form['user']).first():
            flash("Please choose a different Username")
        else:
            newuser.save()
            return "Signed Up Successfull"
    return redirect(url_for('signup'))
if __name__ == '__main__':
    app.run(debug=True)
