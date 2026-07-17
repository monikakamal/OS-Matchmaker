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

# --- USER DATABASE MODEL ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    xp = db.Column(db.Integer, default=3800)       # Default starting XP
    level = db.Column(db.Integer, default=15)      # Default starting Level
    points = db.Column(db.Integer, default=120)    # Added to match leaderboard/index
    avatar = db.Column(db.String(10), default='👤')  # Added for template rendering
    title = db.Column(db.String(50), default='Open Source Novice') # Custom title for rank row

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---

@app.route('/')
def home():
    # 1. Home page needs top 2 issues to showcase spotlight feed
    lang = 'python'
    url = f"https://api.github.com/search/issues?q=label:good-first-issue+language:{lang}&sort=updated"
    issues = []
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            issues = response.json().get('items', [])[:2] # Strictly fetching top 2 for home spotlight
    except Exception as e:
        print(f"DEBUG: Home issues fetch error - {e}")

    # 2. Gamified Badges Inventory (Pass to index.html)
    badges = [
        {"icon": "🐍", "name": "Pythonist", "status": "unlocked"},
        {"icon": "☕", "name": "Java Guru", "status": "locked"},
        {"icon": "🛡️", "name": "Sec-Hero", "status": "locked"},
        {"icon": "🚀", "name": "Contributor", "status": "unlocked"}
    ]
    return render_template('index.html', user=current_user, issues=issues, badges=badges)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Prevent Duplicate User Creation
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Sahi username chunein.")
            return redirect(url_for('register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and bcrypt.check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password")
    return render_template('login.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            user.password = bcrypt.generate_password_hash(request.form.get('new_password')).decode('utf-8')
            db.session.commit()
            flash("Password updated successfully! Ab login karein.")
            return redirect(url_for('login'))
        else:
            flash("User nahi mila!")
    return render_template('reset_password.html')

# --- NAYE STEP ROUTES YAHAN HAIN ---

@app.route('/setup')
def setup():
    return render_template('setup.html', user=current_user)

@app.route('/explore')
def explore():
    lang = request.args.get('lang', 'python')
    url = f"https://api.github.com/search/issues?q=label:good-first-issue+language:{lang}&sort=updated"
    
    issues = []
    try:
        response = requests.get(url, timeout=5)
        print(f"DEBUG: Status Code - {response.status_code}") 
        
        if response.status_code == 200:
            issues = response.json().get('items', [])[:6]
    except Exception as e:
        print(f"ERROR: {e}")
        
    return render_template('explore.html', user=current_user, issues=issues, current_lang=lang)

@app.route('/fix')
def fix():
    return render_template('fix.html', user=current_user)

@app.route('/submit')
def submit():
    # Step 4 ke liye route add kar diya hai taaki error na aaye
    return render_template('submit.html', user=current_user)

# --- END NAYE ROUTES ---

@app.route('/leaderboard')
def leaderboard():
    # Fetch all users sorted by XP descending to make leaderboard live
    users = User.query.order_by(User.xp.desc()).all()
    
    # Restructure data matching the keys in leaderboard.html
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
    return render_template('leaderboard.html', user=current_user, leaderboard_data=leaderboard_data)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Is block ko humne bahar nikal diya taaki Render par bhi database ban sake
with app.app_context():
    db.create_all() # Generates database schema on start automatically

if __name__ == '__main__':
    app.run(debug=True)