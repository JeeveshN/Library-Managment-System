from flask import Flask,render_template,redirect,url_for,request,flash,session
from flask.ext.mongoalchemy import MongoAlchemy
import re

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
    email=db1.StringField()

class Book(db1.Document):
    name=db1.StringField()
    author=db1.StringField()
    quantity=db1.IntField()
    section=db1.StringField()
    serialno=db1.IntField()

class Information(db1.Document):
    User=db1.DocumentField(User_Login)
    books=db1.ListField(db1.DictField(db1.StringField()))


class Admin(db1.Document):
    username=db1.StringField()
    password=db1.StringField()

if not Admin.query.filter(Admin.username=='admin').first():
    Admin=Admin(username='admin',password='admin')
    Admin.save()

def check_admin():
    if 'username' in session:
        username=session['username']
        if username==Admin.query.one().username:
            return True
    return False

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
    if check_admin():
        return render_template("admin.html")
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

@app.route('/all_books')
def all_books():
    if check_admin():
        return render_template('all.html',books=Book.query.all())
    else:
        return redirect(url_for('admin123'))

@app.route('/add')
def add():
    if check_admin():
        return render_template('add-books.html')
    else:
        return redirect(url_for('admin123'))

@app.route('/add_books',methods=['POST','GET'])
def add_books():
    if check_admin():
        if request.method == 'POST':
            if not request.form['name'] or not request.form['author'] or not request.form['quantity'] or not request.form['section'] or not request.form['serialno']:
                flash("Please Fill All Fields")
                return render_template('add-books.html')
            elif Book.query.filter(Book.name==request.form['name']).first() and Book.query.filter(Book.author==request.form['author']).first():
                book=Book.query.filter(Book.name==request.form['name']).first()
                book.quantity=book.quantity+int(request.form['quantity'])
                book.save()
                flash("The Book has been Successfully Added")
            else:
                book=Book(name=request.form['name'],author=request.form['author'],quantity=int(request.form['quantity']),section=request.form['section'],serialno=int(request.form['serialno']))
                book.save()
                flash("The Book has been Successfully Added")
    return redirect(url_for('admin123'))
#@app.route('/delete_all',methods=['POST','GET'])
##def delete_all():
##    for book in Book.query.all():
##        book.remove()
##    return redirect(url_for('all_books'))
@app.route('/search',methods=['POST','GET'])
def search():
    if check_admin():
        if request.method == 'POST':
            Query=request.form['search']
            if  'author' in Query:
                q=re.findall('(.+)-author',Query)
                return render_template("all.html",books=Book.query.filter(Book.author.regex(q[0]) ).all())
            elif 'title'in Query:
                q=re.findall('(.+)-title',Query)
                return render_template("all.html",books=Book.query.filter(Book.name.regex(q[0]) ).all())
            else:
                return render_template("all.html",books=Book.query.filter(Book.name.regex(Query)).all()+Book.query.filter(Book.author.regex(Query)).all())
    return redirect(url_for('admin123'))
if __name__ == '__main__':
    app.run(debug=True)
