from flask import render_template, request, redirect, session, flash, jsonify
from app import app, db, mail
from app.models import User
from flask_mail import Message
import random
from passlib.hash import bcrypt

# In-memory storage for OTPs
otp_storage = {}

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if User.query.filter_by(email=email).first():
            flash('Email address already exists.')
            return redirect('/register')

        otp = random.randint(100000, 999999)
        otp_storage[email] = otp

        msg = Message('Your OTP Code', sender='python@networkershome.com', recipients=[email])
        msg.body = f'Your OTP code is {otp}'
        mail.send(msg)
        
        session['registration_name'] = name
        session['registration_email'] = email
        session['registration_password'] = password
        
        return redirect('/verify_otp')
    
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session.get('registration_email')
        
        if email and otp and otp_storage.get(email) == int(otp):
            del otp_storage[email]
            
            name = session.get('registration_name')
            password = session.get('registration_password')
            
            if name and password:
                user = User(name=name, email=email, password=password)
                db.session.add(user)
                db.session.commit()
            
            session.pop('registration_name', None)
            session.pop('registration_email', None)
            session.pop('registration_password', None)
            
            flash('OTP verified successfully. You are now registered. Please log in.')
            return redirect('/login')
        else:
            flash('Invalid OTP or email.')
            return redirect('/verify_otp')
    
    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            session.permanent = True
            flash('Login successful.')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password.')
            return redirect('/login')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        flash('You need to log in first.')
        return redirect('/login')
    
    user = User.query.filter_by(email=session['email']).first()
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.')
    return redirect('/login')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form.get('email')
        new_password = request.form.get('new_password')

        user = User.query.filter_by(email=email).first()

        if user:
            user.password = bcrypt.hash(new_password)
            db.session.commit()
            flash('Password has been updated.')
            return redirect('/login')
        else:
            flash('Email address not found.')
            return redirect('/reset_password')

    return render_template('reset_password.html')

@app.route('/send_otp', methods=['POST'])
def send_otp():
    email = request.form.get('email')
    otp = random.randint(100000, 999999)
    otp_storage[email] = otp
    
    session['registration_email'] = email
    
    msg = Message('Your OTP Code', sender='python@networkershome.com', recipients=[email])
    msg.body = f'Your OTP code is {otp}'
    mail.send(msg)
    
    flash('OTP sent to your email.')
    return redirect('/verify_otp')

@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')
    
    if otp_storage.get(email) == int(otp):
        del otp_storage[email]
        return jsonify({'status': 'OTP validated successfully'})
    else:
        return jsonify({'status': 'Invalid OTP'}), 400
