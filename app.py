# Import Section
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient

app = Flask(__name__)

# Connect to local MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['hand_2_write']  # Database name

# Home route - shows the form/page
@app.route('/')
def index():
    return render_template('index.html')

# Route to test DB connection
@app.route('/db')
def test_db():
    return "MongoDB connected successfully!"

# Route to handle form submission (POST)
@app.route('/add_user', methods=['POST'])
def add_user():
    data = request.form.to_dict()
    db.users.insert_one(data)  # Insert into 'users' collection
    return "User added successfully!"  # Or redirect back with a message

if __name__ == '__main__':
    app.run(debug=True)

