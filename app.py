from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId
import re  # Import the re module for email validation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['hand_2_write']
users_collection = db['users']

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class MongoUser(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.role = user_data.get('role')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.date_joined = user_data.get('date_joined')

    def __repr__(self):
        return f"MongoUser('{self.username}', '{self.email}', '{self.role}')"

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        return MongoUser(user)
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')

@app.route('/register', methods=['POST'])
def register():
    role = request.form.get('userType')
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')

    if not all([role, username, email, password, confirm_password, first_name, last_name]):
        return render_template('signup.html', error='All basic fields are required.')
    if password != confirm_password:
        return render_template('signup.html', error='Passwords do not match.')
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return render_template('signup.html', error='Invalid email format.')

    if users_collection.find_one({'username': username, 'role': role}):
        return render_template('signup.html', error=f'Username already taken for the role of {role}.')
    if users_collection.find_one({'email': email, 'role': role}):
        return render_template('signup.html', error=f'Email address already registered for the role of {role}.')

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    date_joined = datetime.utcnow()

    user_data = {
        'role': role,
        'username': username,
        'email': email,
        'password': hashed_password,
        'date_joined': date_joined,
        'firstName': first_name,
        'lastName': last_name
    }

    user_id = users_collection.insert_one(user_data).inserted_id

    if role == 'disabled':
        disabled_data = {
            'user_id': user_id,  # Store as ObjectId
            'mobile': request.form.get('mobile'),
            'firstName': request.form.get('firstName'),
            'lastName': request.form.get('lastName'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender'),
            'city': request.form.get('city'),
            'district': request.form.get('district'),
            'state': request.form.get('state'),
            'pincode': request.form.get('pincode'),
            'disability_type': request.form.get('disability_type'),
            'employment_status': request.form.get('disabledEmploymentStatus'),
            'organization': request.form.get('organization'),
            'designation': request.form.get('designation'),
            'current_qualification': request.form.get('current_qualification'),
            'current_institution': request.form.get('current_institution'),
            'current_year': request.form.get('current_year'),
            'highest_qualification': request.form.get('highest_qualification'),
            'highest_institution': request.form.get('highest_institution'),
            'highest_year': request.form.get('highest_year'),
            'email_pref': request.form.get('email_pref') == 'on',
            'sms_pref': request.form.get('sms_pref') == 'on',
            'screen_reader': request.form.get('screen_reader') == 'on',
            'high_contrast': request.form.get('high_contrast') == 'on',
            'exam_date': request.form.get('exam_date'),
            'exam_name': request.form.get('exam_name'),
            'exam_qualification': request.form.get('exam_qualification'),
            'exam_center': request.form.get('exam_center'),
            'exam_language': request.form.get('exam_language')
        }
        users_collection.insert_one(disabled_data)

    elif role == 'writer':
        writer_data = {
            'user_id': user_id,  # Store as ObjectId
            'mobile': request.form.get('mobile'),
            'firstName': request.form.get('firstName'),
            'lastName': request.form.get('lastName'),
            'dob': request.form.get('dob'),
            'gender': request.form.get('gender'),
            'city': request.form.get('city'),
            'district': request.form.get('district'),
            'state': request.form.get('state'),
            'pincode': request.form.get('pincode'),
            'language_type': request.form.get('language_type'),
            'employment_status': request.form.get('employment_status'),
            'organization': request.form.get('organization'),
            'designation': request.form.get('designation'),
            'current_qualification': request.form.get('current_qualification'),
            'current_institution': request.form.get('current_institution'),
            'current_year': request.form.get('current_year'),
            'highest_qualification': request.form.get('highest_qualification'),
            'highest_institution': request.form.get('highest_institution'),
            'highest_year': request.form.get('highest_year'),
            'email_pref': request.form.get('email_pref') == 'on',
            'sms_pref': request.form.get('sms_pref') == 'on'
        }
        users_collection.insert_one(writer_data)

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_type = request.form.get('type')

        user = users_collection.find_one({'username': username, 'role': user_type})

        if user and check_password_hash(user['password'], password):
            mongo_user = MongoUser(user)
            login_user(mongo_user)
            session['user_id'] = str(user['_id'])
            session['role'] = user['role']
            return jsonify({'message': 'Login successful!', 'role': user['role']})
        else:
            return jsonify({'error': 'Invalid username, password, or user type'}), 401
    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile/')
@login_required
def profile():
    user_role = session.get('role')
    if user_role == 'disabled':
        return render_template('dcprofile.html')
    elif user_role == 'writer':
        return render_template('wprofile.html')
    else:
        return "Invalid user role."

@app.route('/api/writer-profile')
@login_required
def get_writer_profile():
    user_id = session.get('user_id')
    main_user_data = users_collection.find_one({'_id': ObjectId(user_id), 'role': 'writer'})
    writer_profile_data = users_collection.find_one({'user_id': ObjectId(user_id)})

    if main_user_data and writer_profile_data:
        profile = {
            'name': f"{main_user_data.get('firstName', '')} {main_user_data.get('lastName', '')}",
            'age': main_user_data.get('dob'),
            'gender': main_user_data.get('gender'),
            'mobile': writer_profile_data.get('mobile'),
            'email': main_user_data.get('email'),
            'pincode': writer_profile_data.get('pincode'),
            'state': writer_profile_data.get('state'),
            'district': writer_profile_data.get('district'),
            'cityVillage': writer_profile_data.get('city'),
            'writingPreferences': writer_profile_data.get('language_type'),
            'communicationLanguage': writer_profile_data.get('language_type'),
            'currentQualification': writer_profile_data.get('current_qualification'),
            'currentInstitution': writer_profile_data.get('current_institution'),
            'currentCompletionYear': writer_profile_data.get('current_year'),
            'employmentStatus': writer_profile_data.get('employment_status'),
            'organization': writer_profile_data.get('organization'),
            'designation': writer_profile_data.get('designation'),
            'sector': writer_profile_data.get('sector'),
            'highestQualification': writer_profile_data.get('highest_qualification'),
            'highestInstitution': writer_profile_data.get('highest_institution'),
            'highestCompletionYear': writer_profile_data.get('highest_year'),
            'profilePicture': 'https://via.placeholder.com/150'
        }
        return jsonify(profile)
    else:
        return jsonify({'error': 'Writer profile not found'}), 404

@app.route('/api/dc-profile')
@login_required
def get_dc_profile():
    user_id = session.get('user_id')
    main_user_data = users_collection.find_one({'_id': ObjectId(user_id), 'role': 'disabled'})
    dc_profile_data = users_collection.find_one({'user_id': ObjectId(user_id)})

    if main_user_data and dc_profile_data:
        profile = {
            'name': f"{main_user_data.get('firstName', '')} {main_user_data.get('lastName', '')}",
            'age': main_user_data.get('dob'),
            'gender': main_user_data.get('gender'),
            'pincode': dc_profile_data.get('pincode'),
            'state': dc_profile_data.get('state'),
            'district': dc_profile_data.get('district'),
            'cityVillage': dc_profile_data.get('city'),
            'mobile': dc_profile_data.get('mobile'),
            'email': main_user_data.get('email'),
            'disableType': dc_profile_data.get('disability_type'),
            'currentEducation': {
                'highestQualification': dc_profile_data.get('current_qualification'),
                'institution': dc_profile_data.get('current_institution'),
                'yearOfCompletion': dc_profile_data.get('current_year')
            },
            'employment': {
                'status': dc_profile_data.get('employment_status'),
                'organization': dc_profile_data.get('organization'),
                'designation': dc_profile_data.get('designation')
            },
            'highestEducation': {
                'highestQualification': dc_profile_data.get('highest_qualification'),
                'institution': dc_profile_data.get('highest_institution'),
                'yearOfCompletion': dc_profile_data.get('highest_year')
            },
            'preferences': {
                'communication': 'Email' if dc_profile_data.get('email_pref') else 'SMS' if dc_profile_data.get('sms_pref') else 'None',
                'accessibility': ', '.join(filter(None, [
                    'Screen Reader' if dc_profile_data.get('screen_reader') else None,
                    'High Contrast' if dc_profile_data.get('high_contrast') else None
                ])),
                'languageType': dc_profile_data.get('exam_language')
            },
            'examInfo': {
                'date': dc_profile_data.get('exam_date'),
                'name': dc_profile_data.get('exam_name'),
                'minQualification': dc_profile_data.get('exam_qualification'),
                'center': dc_profile_data.get('exam_center'),
                'languageType': dc_profile_data.get('exam_language')
            },
            'profilePic': 'https://via.placeholder.com/150'
        }
        return jsonify(profile)
    else:
        return jsonify({'error': 'Disabled candidate profile not found'}), 404

@app.route('/welcome')
@login_required
def welcome():
    return "Welcome to the protected area!"

if __name__ == '__main__':
    app.run(debug=True)