from flask import Flask,render_template,redirect,url_for,request,flash,session
from flask_mongoalchemy import MongoAlchemy
import datetime
import re

app=Flask(__name__)
#app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///User_Login.sqlite3'
app.config['MONGOALCHEMY_DATABASE'] = 'library'
app.config['SECRET_KEY']='Je123'

db1=MongoAlchemy(app)

class Book(db1.Document):
    name=db1.StringField()
    author=db1.StringField()
    quantity=db1.IntField()
    section=db1.StringField()
    serialno=db1.IntField()
    issued_on=db1.DateTimeField()
    to_be_returned=db1.DateTimeField()
    issued_by=db1.StringField()

class User_Login(db1.Document):
    name= db1.StringField()
    username= db1.StringField()
    password= db1.StringField()
    number= db1.IntField()
    email=db1.StringField()
    books=db1.ListField(db1.IntField(),db_field='Books')

class Admin(db1.Document):
    username=db1.StringField()
    password=db1.StringField()

if not Admin.query.filter(Admin.username=='admin').first():
    Admin=Admin(username='admin',password='admin')
    Admin.save()

def check_admin():
    if 'admin' in session:
        admin=session['admin']
        if admin==Admin.query.one().username:
            return True
    return False

@app.route('/signup')
def signup():
    return render_template('sign-up.html')

@app.route('/')
@app.route('/logged_in',methods=['POST','GET'])
def logged_in():
    if 'user' in session:
        return render_template('logged-in.html',user=session['user'])
    if request.method == 'POST':
        if not request.form['user'] or not request.form['password']:
            flash('Please Fill All The Details')
            return render_template('login.html')
        user=User_Login.query.filter(User_Login.username==request.form['user']).first()
        if not user:
            flash('Please Sign Up First')
        elif user.password != request.form['password']:
            flash('Please enter the correct details')
        else:
            print user.name
            session['user']=user.username
            return render_template('logged-in.html',user=User_Login.query.filter(User_Login.username==request.form['user']).first())
    return render_template('login.html')

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
            newuser=User_Login(name=request.form["name"],username=request.form["user"],password=request.form["password"],number=long(request.form["number"])
            ,email=request.form['email'],books=list())
            newuser.save()
            return "Signed Up Successfull"
    return redirect(url_for('signup'))

@app.route('/admin123')
def admin123():
    if check_admin():
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
            session['admin']=potential_admin.username
            return render_template("admin.html")
    return render_template("admin-login.html")

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin',None)
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
                book=Book(name=request.form['name'],author=request.form['author'],quantity=int(request.form['quantity']),section=request.form['section'],serialno=int(request.form['serialno']),
                issued_on=datetime.datetime.now(),to_be_returned=datetime.datetime.now(),issued_by=Admin.query.one().username)
                book.save()
                flash("The Book has been Successfully Added")
    return redirect(url_for('admin123'))
#@app.route('/delete_all',methods=['POST','GET'])
#def delete_all():
#    for book in Book.query.all():
#        book.remove()
#    return redirect(url_for('all_books'))
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
@app.route('/all_books_users')
def all_books_users():
    if 'user' in session:
        return render_template('User-Avail-Books.html',books=Book.query.all())
    return redirect(url_for('logged_in'))

@app.route('/user_logout')
def user_logout():
    session.pop('user',None)
    return redirect(url_for('logged_in'))

@app.route('/issue_book')
def issue_book():
    if check_admin():
        return render_template('issue-book.html')
    return redirect(url_for('admin123'))

@app.route('/search_issue',methods=['POST','GET'])
def search_issue():
    if check_admin():
        if request.method == 'POST':
            if not request.form['search']:
                flash('Fill The Fields')
            else:
                Query=request.form['search']
                if  'author' in Query:
                    q=re.findall('(.+)-author',Query)
                    return render_template("issue-book.html",books=Book.query.filter(Book.author.regex(q[0]) ).all())
                elif 'title'in Query:
                    q=re.findall('(.+)-title',Query)
                    return render_template("issue-book.html",books=Book.query.filter(Book.name.regex(q[0]) ).all())
                else:
                    return render_template("issue-book.html",books=Book.query.filter(Book.name.regex(Query)).all()+Book.query.filter(Book.author.regex(Query)).all())
        return redirect(url_for('issue_book'))
    return redirect(url_for('admin123'))
@app.route('/book_issued',methods=['POST','GET'])
def book_issued():
    if check_admin():
        if request.method == 'POST':
            if not request.form['username'] or not request.form['serialno']:
                flash('Please Fill All The Fields')
            elif Book.query.filter(Book.serialno==int(request.form['serialno'])).first().quantity==0:
                flash('The Book Is Not Available')
            else:
                user=User_Login.query.filter(User_Login.username==request.form['username']).first()
                user.books.append(int(request.form['serialno']))
                user.save()
                flash('Book Successfully Issued')
                return redirect(url_for('admin'))
            return render_template('issue-book.html')
    return redirect(url_for('admin'))
if __name__ == '__main__':
    app.run(debug=True)
