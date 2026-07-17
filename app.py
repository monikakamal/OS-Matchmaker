from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import requests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'monika_secret_key_123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# ---------------- USER MODEL ----------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    xp = db.Column(db.Integer, default=3800)
    level = db.Column(db.Integer, default=15)
    points = db.Column(db.Integer, default=120)
    avatar = db.Column(db.String(10), default='👤')
    title = db.Column(db.String(50), default='Open Source Novice')
@login_manager.user_loader
def load_user(user_id):   
     return User.query.get(int(user_id))
    # ---------------- HOME PAGE ----------------

@app.route('/')
def home():
    lang = 'python'
    url = f"https://api.github.com/search/issues?q=label:good-first-issue+language:{lang}&sort=updated"

    issues = []

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            issues = response.json().get('items', [])[:2]

    except Exception as e:
        print(f"DEBUG: Home issues fetch error - {e}")

    badges = [
        {
            "icon": "🐍",
            "name": "Pythonist",
            "status": "unlocked"
        },
        {
            "icon": "☕",
            "name": "Java Guru",
            "status": "locked"
        },
        {
            "icon": "🛡️",
            "name": "Sec-Hero",
            "status": "locked"
        },
        {
            "icon": "🚀",
            "name": "Contributor",
            "status": "unlocked"
        }
    ]

    return render_template(
        'index.html',
        user=current_user,
        issues=issues,
        badges=badges
    )
# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists! Please choose another username.")
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            username=username,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.")
        return redirect(url_for('login'))

    return render_template('register.html')
# ---------------- LOGIN ----------------

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for('home'))

        flash("Invalid username or password")

    return render_template('login.html')
# ---------------- RESET PASSWORD ----------------

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():

    if request.method == 'POST':

        username = request.form.get('username')
        new_password = request.form.get('new_password')

        user = User.query.filter_by(username=username).first()

        if user:

            hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_password

            db.session.commit()

            flash("Password updated successfully! Please login.")
            return redirect(url_for('login'))

        else:
            flash("User not found!")

    return render_template('reset_password.html')
# ---------------- SETUP PAGE ----------------

@app.route('/setup')
@login_required
def setup():
    return render_template(
        'setup.html',
        user=current_user
    )
# ---------------- EXPLORE PAGE ----------------

@app.route('/explore')
@login_required
def explore():

    lang = request.args.get('lang', 'python')

    url = f"https://api.github.com/search/issues?q=label:good-first-issue+language:{lang}&sort=updated"

    issues = []

    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            issues = response.json().get('items', [])[:6]

    except Exception as e:
        print(f"GitHub API Error: {e}")

    return render_template(
        'explore.html',
        user=current_user,
        issues=issues,
        current_lang=lang
    )
# ---------------- BUGS PAGE ----------------

@app.route('/bugs')
@login_required
def bugs():

    return render_template(
        'bugs.html',
        user=current_user
    )
# ---------------- FIX PAGE ----------------

@app.route('/fix')
@login_required
def fix():

    return render_template(
        'fix.html',
        user=current_user
    )
# ---------------- SUBMIT PAGE ----------------

@app.route('/submit')
@login_required
def submit():

    return render_template(
        'submit.html',
        user=current_user
    )
# ---------------- LEADERBOARD ----------------

@app.route('/leaderboard')
@login_required
def leaderboard():

    users = User.query.order_by(User.xp.desc()).all()

    leaderboard_data = []

    for index, u in enumerate(users):

        leaderboard_data.append({
            "name": u.username,
            "username": u.username,
            "rank": index + 1,
            "avatar": u.avatar,
            "xp": u.xp,
            "points": u.points,
            "title": u.title
        })

    return render_template(
        'leaderboard.html',
        user=current_user,
        leaderboard_data=leaderboard_data
    )
# ---------------- LOGOUT ----------------

@app.route('/logout')
@login_required
def logout():

    logout_user()
    flash("Logged out successfully!")

    return redirect(url_for('login'))
# ---------------- RUN APP ----------------

if __name__ == '__main__':
    app.run(debug=True)