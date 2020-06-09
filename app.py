from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login=LoginManager(app)
login.login_view='login'

CLASSES = {
    'SAT Tutoring' : {
        'name': 'SAT Tutoring',
        'price': 'insert price here',
        'time': 'insert times here',
    },
    'Debate' : {
        'name': 'Debate',
        'price': 'insert price here',
        'time': 'insert times here',
    },
    'Advanced Math' : {
        'name': 'Advanced Math',
        'price': 'insert price here',
        'time': 'insert times here',
    },
    'Writing and Grammar' : {
        'name': 'Writing and Grammar',
        'price': 'insert price here',
        'time': 'insert times here',
    }
}

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    classes = db.relationship('Classes', backref='Client', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def set_password(self, password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_classes(self):
        return Classes.query.filter(Classes.user_id==self.id)

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Classes {}>'.format(self.name)

from forms import LoginForm, RegistrationForm, EmptyForm

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

@app.route('/home')
def home():
    return render_template ('home.html')

@app.route('/profile')
@login_required
def profile():
    return redirect(url_for('user', user=current_user.username))

@app.route('/user/<user>')
@login_required
def user(user):
    classeS=current_user.check_classes().all()
    return render_template ('profile.html', classlist=classeS)

@app.route('/aboutus')
def aboutus():
    return render_template ('aboutus.html')

@app.route('/classes', methods=['GET', 'POST'])
def classes():
    form = EmptyForm()
    return render_template ('classes.html', classes=CLASSES, form=form)

@app.route('/signup/<classname>', methods=['GET', 'POST'])
@login_required
def signup(classname):
    flash('You have signed up for '+classname)
    c=Classes(name=classname, Client=current_user)
    db.session.add(c)
    db.session.commit()
    return redirect(url_for('classes'))

@app.route('/')
def blank():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page=request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page=url_for('home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))