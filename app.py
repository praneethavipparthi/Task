from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///4ds_clinic.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Create directories if they don't exist
os.makedirs('static/uploads', exist_ok=True)
os.makedirs('templates', exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    profile_picture = db.Column(db.String(200), default='default.jpg')
    address_line1 = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        address_line1 = request.form.get('address_line1')
        city = request.form.get('city')
        state = request.form.get('state')
        pincode = request.form.get('pincode')

        if not all([first_name, last_name, username, email, password, confirm_password, user_type, address_line1, city, state, pincode]):
            flash('All fields are required!', 'error')
            return render_template('signup.html')

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('signup.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('signup.html')

        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return render_template('signup.html')

        profile_picture = 'default.jpg'
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture = filename

        user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            user_type=user_type,
            profile_picture=profile_picture,
            address_line1=address_line1,
            city=city,
            state=state,
            pincode=pincode
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Welcome to 4DS Clinic!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome to 4DS Clinic, {user.first_name}!', 'success')
            if user.user_type == 'patient':
                return redirect(url_for('patient_dashboard'))
            else:
                return redirect(url_for('doctor_dashboard'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')

@app.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.user_type != 'patient':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    return render_template('patient_dashboard.html', user=current_user)

@app.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.user_type != 'doctor':
        flash('Access denied!', 'error')
        return redirect(url_for('login'))
    return render_template('doctor_dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out from 4DS Clinic.', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("4DS Clinic Database initialized successfully!")
    
    print("Starting 4DS Clinic Application...")
    print("Access the application at: http://127.0.0.1:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)