from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pymongo
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['hand2write']
writerDb = db['writer']
disablePersonDb = db['disable_person']
disablePersonExamInfoDb = db['disablePersonExamInfo']
notificationsDb = db['notifications']

# Home page
@app.route("/")
@app.route("/index")
def home():
    return render_template("index.html")
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if email exists in writer collection
        writer = writerDb.find_one({'email': email})
        if writer:
            if writer['password'] == password:
                session['email'] = writer['email']
                session['type'] = 'writer'
                flash("Login successful! Welcome Writer.", "success")
                return redirect(url_for('profile'))
            else:
                flash("Invalid credentials. Please check your email ID and password again.", "danger")
                return render_template("login.html")
        else:
            # Check if email exists in disabled_person collection
            disabled_user = disablePersonDb.find_one({'email': email})
            if disabled_user:
                if disabled_user['password'] == password:
                    session['email'] = disabled_user['email']
                    session['type'] = 'disabled'
                    flash("Login successful! Welcome Disabled Candidate.", "success")
                    return redirect(url_for('profile'))
                else:
                    flash("Invalid credentials. Please check your email ID and password again.", "danger")
                    return render_template("login.html")
            else:
                flash("User not found. Please register.", "warning")
                return render_template("login.html")

    return render_template("login.html")

# Signup page
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_type = request.form.get('type')  # "writer" or "disabled"
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        district = request.form.get('city')       # Value from "City" input (label: District)
        state = request.form.get('district')     # Value from "District" input (label: State)
        pincode = request.form.get('state')     # Value from "State" input (label: PIN-CODE)
        password = request.form.get('password')

        # Check if user already exists in either collection
        if writerDb.find_one({'email': email}) or disablePersonDb.find_one({'email': email}):
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))

        user_data = {
            'type': user_type,
            'name': name,
            'age': age,
            'gender': gender,
            'mobile': mobile,
            'email': email,
            'district': district,
            'state': state,
            'pincode': pincode,
            'password': password
        }

        try:
            if user_type == 'writer':
                writerDb.insert_one(user_data)
            elif user_type == 'disabled':
                disablePersonDb.insert_one(user_data)
            else:
                flash("Invalid user type selected.", "danger")
                return redirect(url_for('register'))

            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except PyMongoError as e:
            flash(f"Database error during registration: {e}", "danger")
            return redirect(url_for('register'))

    return render_template("register.html")

# Profile page
@app.route("/profile")
def profile():
    if 'email' not in session or 'type' not in session:
        flash("You must log in first.", "warning")
        return redirect(url_for('login'))

    email = session['email']
    user_type = session['type']

    if user_type == 'writer':
        user = writerDb.find_one({'email': email})
        notifications = list(notificationsDb.find({'recipient_id': user['_id']}))
        return render_template("wprofile.html", user=user, notifications=notifications)
    elif user_type == 'disabled':
        user = disablePersonDb.find_one({'email': email})
        latest_exam = disablePersonExamInfoDb.find_one(
            {'disabled_person_id': user['_id']},
            sort=[('_id', pymongo.DESCENDING)]
        )

        nearby_writers = []
        if latest_exam and 'pin_code' in latest_exam:
            nearby_writers = list(writerDb.find({
                'pincode': latest_exam['pin_code'] # Now searching by pincode only
            }))

        notification_status = {}
        if latest_exam:
            notifications_sent = notificationsDb.find({
                'sender_id': user['_id'],
                'exam_details.pin_code': latest_exam['pin_code'],
                'status': 'accepted'
            })
            for notification in notifications_sent:
                notification_status[str(notification['recipient_id'])] = 'accepted'

        return render_template("dcprofile.html", user=user, nearby_writers=nearby_writers, notification_status=notification_status)
    else:
        flash("Invalid user type in session.", "danger")
        return redirect(url_for('logout'))

# Add exam information
@app.route("/add_exam_info", methods=['POST'])
def add_exam_info():
    if 'email' not in session or session['type'] != 'disabled':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('login'))

    email = session['email']
    disabled_user = disablePersonDb.find_one({'email': email})
    if not disabled_user:
        flash("User not found.", "danger")
        return redirect(url_for('profile'))

    exam_details = {
        'disabled_person_id': disabled_user['_id'],
        'date': request.form.get('exam_date'),
        'name': request.form.get('exam_name'),
        'qualification': request.form.get('min_qualification'),
        'center': request.form.get('exam_center'),
        'pin_code': request.form.get('pin_code'),
        'notification_sent': False
    }

    try:
        disablePersonExamInfoDb.insert_one(exam_details)
        flash("Exam details added successfully!", "success")
    except PyMongoError as e:
        flash(f"Database error: {e}", "danger")

    return redirect(url_for('profile'))

# Send notification to writer
@app.route("/send_notification", methods=['POST'])
def send_notification():
    if 'email' not in session or session['type'] != 'disabled':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        writer_id_str = data.get('writer_id')
        if not writer_id_str:
            return jsonify({'success': False, 'message': 'Writer ID not provided'}), 400

        writer_id = ObjectId(writer_id_str)
        disabled_user = disablePersonDb.find_one({'email': session['email']})
        writer = writerDb.find_one({'_id': writer_id})

        if not disabled_user or not writer:
            return jsonify({'success': False, 'message': 'Invalid user or writer'}), 404

        latest_exam_info = disablePersonExamInfoDb.find_one(
            {'disabled_person_id': disabled_user['_id']},
            sort=[('_id', pymongo.DESCENDING)]
        )

        if latest_exam_info:
            notification_data = {
                'recipient_id': writer_id,
                'sender_id': disabled_user['_id'],
                'sender_name': disabled_user['name'],
                'exam_details': {
                    'name': latest_exam_info.get('name'),
                    'date': latest_exam_info.get('date'),
                    'center': latest_exam_info.get('center'),
                    'pin_code': latest_exam_info.get('pin_code')
                },
                'status': 'pending',
                'timestamp': datetime.utcnow()
            }
            notificationsDb.insert_one(notification_data)

            disablePersonExamInfoDb.update_one(
                {'_id': latest_exam_info['_id']},
                {'$set': {'notification_sent': True}}
            )

            return jsonify({'success': True, 'message': 'Notification sent'}), 200
        else:
            return jsonify({'success': False, 'message': 'No exam details found to send notification'}), 400

    except Exception as e:
        print(f"Error sending notification: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to accept a notification (writer's side)
@app.route("/accept_request", methods=['POST'])
def accept_request():
    if 'email' not in session or session['type'] != 'writer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data = request.get_json()
        notification_id_str = data.get('notification_id')
        if not notification_id_str:
            return jsonify({'success': False, 'message': 'Notification ID not provided'}), 400

        notification_id = ObjectId(notification_id_str)
        writer = writerDb.find_one({'email': session['email']})
        notification = notificationsDb.find_one({'_id': notification_id, 'recipient_id': writer['_id']})

        if not notification:
            return jsonify({'success': False, 'message': 'Notification not found or not for this writer'}), 404

        # Update the notification status to 'accepted'
        notificationsDb.update_one(
            {'_id': notification_id},
            {'$set': {'status': 'accepted', 'accepted': True}}
        )

        # Return the sender's ID (converted to string)
        return jsonify({'success': True, 'message': 'Request accepted', 'sender_id': str(notification['sender_id'])}), 200

    except Exception as e:
        print(f"Error accepting request: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to get the mobile number of the disabled candidate (writer's side)
@app.route("/get_candidate_mobile/<candidate_id_str>")
def get_candidate_mobile(candidate_id_str):
    if 'email' not in session or session['type'] != 'writer':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        candidate_id = ObjectId(candidate_id_str)
        candidate = disablePersonDb.find_one({'_id': candidate_id})

        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found'}), 404

        return jsonify({'success': True, 'mobile': candidate['mobile']}), 200

    except Exception as e:
        print(f"Error fetching candidate mobile: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Route to fetch new notifications (for potential periodic updates on writer's side)
@app.route("/get_notifications")
def get_notifications():
    if 'email' not in session or session['type'] != 'writer':
        return "", 401 # Or redirect

    writer = writerDb.find_one({'email': session['email']})
    if writer:
        notifications = list(notificationsDb.find({'recipient_id': writer['_id']}))
        return render_template('partials/notifications.html', notifications=notifications)
    return "<p class='no-notifications'>No notifications.</p>"

# About page
@app.route("/about")
def about():
    return render_template("about.html")

# Contact page
@app.route("/contact")
def contact():
    return render_template("contact.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('home'))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)