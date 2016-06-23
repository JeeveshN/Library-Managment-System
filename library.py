from flask import Flask,render_template,redirect,url_for,request,flash,session
from flask.ext.mongoalchemy import MongoAlchemy

app=Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///User_Login.sqlite3'
app.config['MONGOALCHEMY_DATABASE'] = 'library'
app.config['SECRET_KEY']='Je123'

db1=MongoAlchemy(app)

class User_Login(db1.Document):
    name= db1.StringField()
    username= db1.StringField()
    password= db1.StringField()
    number= db1.IntField()

class Book(db1.Document):
    name=db1.StringField()
    author=db1.StringField()
    quantity=db1.IntField()
    section=db1.StringField()
    issued_by=db1.ListField(db1.DictField(db1.StringField()))

class Information(db1.Document):
    name=db1.StringField()
    username=db1.StringField()
    books=db1.ListField(db1.DictField(db1.StringField()))

class Admin(db1.Document):
    username=db1.StringField()
    password=db1.StringField()

if not Admin.query.filter(Admin.username=='admin').first():
    Admin=Admin(username='admin',password='admin')
    Admin.save()

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
        if not request.form['name'] or not request.form['user'] or not request.form['password'] or not request.form['rep_password']:
            flash("Fill All The Fields ")
            return redirect(url_for('signup'))
        elif request.form['password'] != request.form['rep_password']:
            flash("Passwords Don't Match")
        elif User_Login.query.filter(User_Login.name==request.form['name']).first() or User_Login.query.filter(User_Login.number==long((request.form['number']))).first():
            flash("User already registered")
        elif User_Login.query.filter(User_Login.username==request.form['user']).first():
            flash("Please choose a different Username")
        else:
            newuser=User_Login(name=request.form["name"],username=request.form["user"],password=request.form["password"],number=long(request.form["number"]))
            newuser.save()
            return "Signed Up Successfull"
    return redirect(url_for('signup'))

@app.route('/admin123')
def admin123():
    if 'username' in session:
        username=session['username']
        if username==Admin.query.one().username:
            return render_template("admin.html")
    return render_template("admin-login.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password']:
            flash("Please fill in All The Fields")
            return render_template("admin-login.html")
        potential_admin=Admin.query.filter(Admin.username==request.form['username']).first()
        if not potential_admin:
            flash('Wrong Details')
        elif potential_admin.password != request.form['password']:
            flash('Wrong Details')
        else:
            session['username']=potential_admin.username
            return render_template("admin.html")
    return render_template("admin-login.html")

@app.route('/admin_logout')
def admin_logout():
    session.pop('username',None)
    return redirect(url_for('admin123'))

if __name__ == '__main__':
    app.run(debug=True)
