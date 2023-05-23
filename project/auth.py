from flask import Blueprint, render_template,redirect,url_for,request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, books
from . import db
from flask_login import login_user,login_required, current_user, logout_user

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    
    if not user or not check_password_hash(user.password, password):
        flash('Incorrect Credentials! Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    else:
        flash('Logged in successfully!', category='success')
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))

@auth.route('/staff_login')
def staff_login():
    return render_template('staff_login.html')

@auth.route('/staff_login', methods=['POST'])
def staff_login_post():
    password = request.form.get('password')
    # password=generate_password_hash(password, method='sha256')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email="library_staff@library.in").first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=remember)
        return redirect(url_for('main.staff_profile'))
     
    else:
        flash('Incorrect Password! Please try again.')
        return redirect(url_for('auth.staff_login'))
        

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    
    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    else:
        
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        flash('Registration completed!', category='success')
        return redirect(url_for('auth.login'))
    
@auth.route('/add_book', methods=['POST'])
def add_book():
    btn = request.form.get("response")
    if btn == "add":
        return render_template('add_book.html')
    elif btn == "remove":
        books_all = books.query.all()
        return render_template('remove.html', books_all=books_all)
    elif btn == "update":
        return render_template('update.html')
    

@auth.route('/add_book_post', methods=['POST'])
def add_book_post():
    book_id = request.form.get('book_id')
    book_name = request.form.get('book_name')
    inventory = request.form.get('inventory')

    book = books.query.filter_by(book_id=book_id).first() # if this returns a user, then the email already exists in database

    if book: # if a book is found, we want to redirect back .
        flash('book already exists. Please update inventory')
        return redirect(url_for('auth.add_book'))
    
    else:
        
        new_book = books(book_id=book_id, book_name=book_name, Inventory=inventory)
       
        db.session.add(new_book)
        db.session.commit()
        flash('book added successfully', category='success')
        return redirect(url_for('main.staff_profile'))
    # return render_template('add_book.html')
    
@auth.route('/<int:book_id>/issue')
# @login_required
def issue(book_id):
    book = books.query.get(book_id)
    ref_no = str(book_id) + str(current_user.id)
    flash(book.book_name + ' issued successfully....your reference number is ' + str(ref_no), category='success')
    return redirect(url_for('main.profile'))

@auth.route('/<int:book_id>/remove')
# @login_required
def remove(book_id):
    book = books.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('main.staff_profile'))

    

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
    # return render_template('logout.html', name = current_user.name)
