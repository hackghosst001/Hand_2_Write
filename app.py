from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["hand_to_write"]
users = db["users"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        role = request.form['role']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        user_data = {
            "role": role,
            "name": name,
            "email": email,
            "phone": phone,
            "password": password
        }

        if role == "Disabled Candidate":
            user_data["aadhar"] = request.form.get("aadhar")
            user_data["education"] = request.form.get("education")
            user_data["disability"] = request.form.get("disability")
        elif role == "Writer":
            user_data["qualification"] = request.form.get("qualification")
            user_data["experience"] = request.form.get("experience")

        users.insert_one(user_data)
        flash("Signup successful!")
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email, 'password': password})
        if user:
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            flash('Login successful!')
            return redirect(url_for('wprofile' if user['role'] == 'Writer' else 'dcprofile'))
        else:
            flash("Invalid email or password.")
    return render_template("login.html")

@app.route('/wprofile')
def wprofile():
    if 'user_id' in session and session.get('role') == 'Writer':
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template("wprofile.html", user=user)
    return redirect(url_for('login'))

@app.route('/dcprofile')
def dcprofile():
    if 'user_id' in session and session.get('role') == 'Disabled Candidate':
        user = users.find_one({'_id': ObjectId(session['user_id'])})
        return render_template("dcprofile.html", user=user)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
