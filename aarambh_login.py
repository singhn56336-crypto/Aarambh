"""
app.py
------
Python Flask Backend for Smart Campus Analytics Platform User Registration & Authentication.
"""
import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart_campus_secret_key_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus_users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------
# DATABASE USER MODEL
# ---------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    campus_id = db.Column(db.String(50), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'faculty'
    department = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create database tables automatically
with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# COMBINED HTML TEMPLATE (TAILWIND CSS)
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AARAMBH</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }
        .glass-card {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">

    <div class="w-full max-w-md space-y-6">
        <!-- Logo Header -->
        <div class="text-center space-y-2">
            <div class="inline-flex p-3 bg-gradient-to-tr from-blue-600 to-indigo-500 rounded-2xl text-white shadow-lg shadow-blue-500/20 mb-2">
                <img src="../image/aarambh.png">
            </div>

            <h1 class="text-2xl font-bold tracking-tight text-white">AARAMBH</h1>
            <p class="text-xs text-slate-400">Student Success & Early Intervention Platform</p>
        </div>

        <!-- Flash Alert Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="p-3 rounded-xl text-xs font-semibold text-center border {% if category == 'error' %} bg-rose-950/80 border-rose-800 text-rose-300 {% else %} bg-emerald-950/80 border-emerald-800 text-emerald-300 {% endif %}">
                {{ message }}
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <!-- Form Container -->
        <div class="glass-card p-6 sm:p-8 rounded-2xl shadow-xl space-y-5">
            
            <!-- Page Title -->
            <div class="text-center border-b border-slate-700/60 pb-3">
                <h2 class="text-lg font-bold text-white">
                    {% if page == 'signup' %} Create an Account {% else %} Sign In to Portal {% endif %}
                </h2>
            </div>

            {% if page == 'signup' %}
            <!-- SIGN UP FORM -->
            <form action="{{ url_for('signup') }}" method="POST" class="space-y-4">
                
                <!-- Role Selector -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Account Role</label>
                    <select name="role" required class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 focus:ring-2 focus:ring-blue-500">
                        <option value="student">Student Portal</option>
                        <option value="faculty">Faculty / Administrator</option>
                    </select>
                </div>

                <!-- Full Name -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Full Name</label>
                    <input type="text" name="full_name" required placeholder="e.g. Rahul Sharma" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <!-- Campus Email -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Campus Email Address</label>
                    <input type="email" name="email" required placeholder="student@campus.edu.in" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <!-- Roll Number / Employee ID -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Student Roll No. / Employee ID</label>
                    <input type="text" name="campus_id" required placeholder="STU-2026-1001" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <!-- Department -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Department</label>
                    <select name="department" required class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 focus:ring-2 focus:ring-blue-500">
                        <option value="Computer Science Engineering">Computer Science Engineering</option>
                        <option value="Information Technology">Information Technology</option>
                        <option value="Electronics & Communication">Electronics & Communication</option>
                        <option value="Mechanical Engineering">Mechanical Engineering</option>
                    </select>
                </div>

                <!-- Password -->
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Password</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg transition">
                    Register Account
                </button>
            </form>

            <div class="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
                Already registered? <a href="{{ url_for('login') }}" class="text-blue-400 hover:underline font-semibold">Sign in here</a>
            </div>

            {% else %}
            <!-- LOGIN FORM -->
            <form action="{{ url_for('login') }}" method="POST" class="space-y-4">
                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Campus Email Address</label>
                    <input type="email" name="email" required placeholder="student@campus.edu.in" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <div>
                    <label class="block text-xs font-medium text-slate-300 mb-1">Password</label>
                    <input type="password" name="password" required placeholder="••••••••" class="w-full px-3 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-blue-500">
                </div>

                <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold text-xs rounded-xl shadow-lg transition">
                    Sign In to Portal
                </button>
            </form>

            <div class="text-center text-xs text-slate-400 pt-2 border-t border-slate-800">
                New user? <a href="{{ url_for('signup') }}" class="text-blue-400 hover:underline font-semibold">Create an account</a>
            </div>
            {% endif %}

        </div>
    </div>

    <script>
        lucide.createIcons();
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# APPLICATION ROUTES
# ---------------------------------------------------------

@app.route('/aarambh_dashboard')
def home():
    if 'user_id' in session:
        return f"""
        <div style="background-color: #0f172a; color: white; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; font-family: sans-serif;">
            <h1>🎓 Welcome to Smart Campus Analytics, {session['user_name']}!</h1>
            <p>Role: {session['user_role'].title()} | Dept: {session['user_dept']}</p>
            <br>
            <a href="/logout" style="color: #3b82f6; text-decoration: underline;">Logout</a>
        </div>
        """
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        campus_id = request.form.get('campus_id')
        role = request.form.get('role')
        department = request.form.get('department')
        password = request.form.get('password')

        # Check if user already exists
        existing_user = User.query.filter((User.email == email) | (User.campus_id == campus_id)).first()
        if existing_user:
            flash('Email or Campus ID already registered. Please login.', 'error')
            return redirect(url_for('signup'))

        # Create new user record
        new_user = User(
            full_name=full_name,
            email=email,
            campus_id=campus_id,
            role=role,
            department=department
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template_string(HTML_TEMPLATE, page='signup')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            session['user_dept'] = user.department
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login'))

    return render_template_string(HTML_TEMPLATE, page='login')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Smart Campus Authentication Server on http://127.0.0.1:5000")
    app.run(debug=True)