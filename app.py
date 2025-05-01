from flask import Flask, render_template, request, redirect, flash, url_for, session
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = 'secret123'  # Needed for flashing messages

client = MongoClient('mongodb://localhost:27017/')
db = client['hand_2_write']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    if data['password'] != data['confirm_password']:
        flash("Passwords do not match!", "error")
        return redirect(url_for('signup'))

    db.users.insert_one(data)
    flash("Your information was submitted successfully!", "success")
    return redirect(url_for('signup'))

@app.route('/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['type']  # Updated to receive dropdown value

    user = db.users.find_one({"username": username, "password": password, "type": user_type})
    if user:
        name = user.get('name', 'User')
        return render_template("welcome.html", name=name)
    else:
        flash("Invalid credentials or user type!", "error")
        return redirect(url_for('login'))

@app.route('/welcome')
def welcome():
    name = session.get('name', 'User')
    return render_template('welcome.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
