from flask import Flask, render_template, request, redirect, session, flash
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.permanent_session_lifetime = timedelta(minutes=10)

users = {}

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        secret = pyotp.random_base32()
        users[email] = {'password': generate_password_hash(password), 'secret': secret}

        otp_uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="SecureLoginSystem")
        session['email'] = email
        session['otp_uri'] = otp_uri

        return render_template('otp.html', otp_uri=otp_uri)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.get(email)
        if user and check_password_hash(user['password'], password):
            session['email'] = email
            return redirect('/verify')
        else:
            flash("Invalid credentials")
    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'email' not in session:
        return redirect('/login')

    if request.method == 'POST':
        otp = request.form['otp']
        user = users.get(session['email'])
        if pyotp.TOTP(user['secret']).verify(otp):
            session['otp_verified_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session['ip'] = request.remote_addr
            session['user_agent'] = request.headers.get('User-Agent')
            session.permanent = True
            return redirect('/dashboard')
        else:
            flash("Invalid OTP")
    return render_template('otp.html', otp_uri=None)

import requests

@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect('/login')

    # Fetch cybersecurity news
    api_key = '0c703825b2644cf0b9ffe13eb95e9a8d'
    url = f'https://newsapi.org/v2/everything?q=cybersecurity&sortBy=publishedAt&apiKey={api_key}'
    try:
        response = requests.get(url)
        articles = response.json().get('articles', [])[:5]  # Show top 5
    except:
        articles = []

    return render_template('dashboard.html', articles=articles)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
