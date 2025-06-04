# Hand2Write ✍️

**Hand2Write** is a web platform that connects **Disabled Candidates** with suitable **Writers** (scribes) for upcoming exams. The platform ensures accessibility, profile-based matching, and secure signup/login workflows.

---

## 🔧 Tech Stack

- **Frontend**: HTML, CSS, JavaScript  
- **Backend**: Flask (Python)  
- **Database**: MongoDB

---

## 🚀 Features

### 👤 User Roles

#### 1. Disabled Candidate
- Fills detailed profile including:
  - Personal & Contact Info
  - Disability Type & Certificate Upload
  - Employment & Education Info
  - Accessibility Preferences
  - Upcoming Exam Details
- Custom Signup Form with Validation

#### 2. Writer
- Provides:
  - Personal & Contact Info
  - Employment & Education Details
  - Writing Preferences
- Signup & Profile Management

---

## 🔐 Login Page

- Dropdown to select role: **Disabled Candidate** or **Writer**
- Role-based login with username and password

---

## 🧾 Profile Pages

- **Disabled Candidate**:
  - Displays all personal and exam details
  - Can add/edit upcoming exams (exam name, date, centre pincode)

- **Writer**:
  - Notification area showing potential matches with candidates

---

## 📌 Matching Logic

- Matches are based on:
  - **Pincode**
  - Candidate preferences: **Minimum Qualification**, **Language Type**, **Gender**

---

## 📁 Folder Structure

```
/hand2write
│
├── templates/        # HTML files
├── static/           # CSS, JS, and images
├── app.py            # Flask backend
├── requirements.txt  # Python dependencies
└── README.md
```

---

## 🛠 Setup Instructions

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your-username/hand2write.git
   cd hand2write
   ```

2. **Create a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**  
   ```bash
   python app.py
   ```

---

## 📄 License

This project is for educational/demo purposes and currently not licensed.

---

## 🙋‍♂️ Author

**Ansu Raj**  
Cybersecurity Engineering Student