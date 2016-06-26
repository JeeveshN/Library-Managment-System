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

class search_object():
    Books=list()
    Users=list()
    query=None

    def __init__(self,books,users,query):
        self.Books=books
        self.Users=users
        self.query=query

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
def get_books(user):
    books=list()
    for sno in user.books:
        books.append(Book.query.filter(Book.serialno==sno).first())
    return books

def search_P(Query):
    if  'author' in Query:
        q=re.findall('(.+)-author',Query)
        books=Book.query.filter(Book.author.regex(q[0]) ).all()
        return search_object(books,list(),None)
    elif 'title'in Query:
        q=re.findall('(.+)-title',Query)
        books=Book.query.filter(Book.name.regex(q[0]) ).all()
        return search_object(books,list(),None)
    elif 'book' in Query:
        books=Book.query.filter(Book.name.regex(Query)).all()+Book.query.filter(Book.author.regex(Query)).all()
        return search_object(books,list(),None)
    elif 'user' in Query:
        q=re.findall('(.+)-user',Query)
        users=User_Login.query.filter(User_Login.username.regex(q[0])).all()
        user=users[0]
        books=get_books(user)
        query='user'
        return search_object(books,users,query)
    elif Query == 'all-user':
        return search_object(books=get_all_books(),users=User_Login.query.all(),query='user')
    else:
        return False


@app.route('/signup')
def signup():
    return render_template('sign-up.html')

@app.route('/')
@app.route('/logged_in',methods=['POST','GET'])
def logged_in():
    if 'user' in session:
        return render_template('logged-in.html',user=User_Login.query.filter(User_Login.username==session['user']).first(),time=None)
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
            session['user']=user.username
            return render_template('logged-in.html',user=User_Login.query.filter(User_Login.username==request.form['user']).first(),time='first')
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
            flash('You Have signed up successfully')
            session['username']=newuser.username
            return render_template('logged-in.html',user=User_Login.query.filter(User_Login.username==request.form['user']).first(),time='first')
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
        for book in Book.query.all():
            print book.name
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
            if search_P(request.form['search']):
                obj=search_P(request.form['search'])
                return render_template("all.html",books=obj.Books,query=obj.query,users=obj.Users)
            else:
                flash('Use [title/author-author for Books] or [Username-user for username]')
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
            if search_P(request.form['search']):
                obj=search_P(request.form['search'])
                return render_template("issue-book.html",books=obj.Books,query=obj.query,users=obj.Users)
            else:
                flash('Use [title/author-author for Books] or [Username-user for username]')
        return redirect(url_for('issue_book'))
    return redirect(url_for('admin123'))
@app.route('/book_issue_return',methods=['POST','GET'])
def book_issue_return():
    if check_admin():
        if request.method == 'POST':
            if not request.form['username'] or not request.form['serialno']:
                flash('Please Fill All The Fields')
            elif not User_Login.query.filter(User_Login.username==request.form['username']).first():
                flash("Username is Wrong")
            if request.form['Submit']=='Issue':
                if Book.query.filter(Book.serialno==int(request.form['serialno'])).first().quantity==0:
                    flash('The Book Is Not Available')
                else:
                    user=User_Login.query.filter(User_Login.username==request.form['username']).first()
                    book=Book.query.filter(Book.serialno==int(request.form['serialno'])).first()
                    book.quantity=book.quantity-1
                    book.issued_on=datetime.datetime.today()
                    date=book.issued_on + datetime.timedelta(days=7,weeks=0,hours=0,minutes=0,milliseconds=0,microseconds=0,seconds=0)
                    book.to_be_returned= date
                    book.save()
                    user.books.append(int(request.form['serialno']))
                    user.save()
                    flash('Book Successfully Issued')
                    return redirect(url_for('admin'))
            else:
                if not Book.query.filter(Book.serialno==int(request.form['serialno'])).first():
                    flash("Serial No. Not In Database")
                elif not int(request.form['serialno']) in User_Login.query.filter(User_Login.username==request.form['username']).first().books:
                    flash("The User never issued this Book")
                else:
                    user=User_Login.query.filter(User_Login.username==request.form['username']).first()
                    user.books.remove(int(request.form['serialno']))
                    user.save()
                    book=Book.query.filter(Book.serialno==int(request.form['serialno'])).first()
                    book.quantity=book.quantity+1
                    book.save()
                    flash('Book Successfully Returned')
                    return redirect(url_for('admin'))
            return render_template('issue-book.html')
    return redirect(url_for('admin'))

@app.route('/change_ad')
def change_ad():
    if check_admin():
        return render_template('change-admin.html')
    return redirect(url_for('admin123'))

@app.route('/change_admin',methods=['POST','GET'])
def change_admin():
    if check_admin():
        if request.method == 'POST':
            if not request.form['username'] or not request.form['prev_pass'] or not request.form['new_pass'] or not request.form['rep_new_pass']:
                flash('Please Fill In All The Fields')
            elif request.form['prev_pass'] != Admin.query.one().password:
                flash('Admin Password is Wrong')
            elif request.form['new_pass'] != request.form['rep_new_pass']:
                flash('Passwords don\'t Match')
            else:
                for admin in Admin.query.all():
                    admin.remove()
                new_admin=Admin(username=request.form['username'],password=request.form['new_pass'])
                new_admin.save()
                flash('Please Login With New Credentials')
                return redirect(url_for('admin_logout'))
    return redirect(url_for('admin123'))
@app.route('/search_user',methods=['POST','GET'])
def search_user():
    if 'username' in session:
        user=User_Login.query.filter(User_Login.username==session['username']).first()
        if request.method == 'POST':
            if search_P(request.form['search']):
                obj=search_P(request.form['search'])
                return render_template("User-Avail-Books.html",books=obj.Books)
    return redirect(url_for('logged_in'))

if __name__ == '__main__':
    app.run(debug=True)
