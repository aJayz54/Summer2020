from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from flask_mail import Mail
from time import time
import jwt

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login=LoginManager(app)
login.login_view='login'
mail=Mail(app)

CLASSES = {
    'A' : {
        'name': 'Intro to Algebra',
        'price': '$10/hr',
        'time': 'Tuesday, Thursday, and Saturday from 2-3:30 PST.',
        'blurb':'Intro Algebra is aimed to introduce students to core concepts that they will engage with in their Algebra classes. Ideas such as systems of equations and inequalities will be explored to help prepare them for the upcoming term.',
    },
    'B' : {
        'name': 'Competition Math: Number Theory',
        'price': '$10/hr',
        'time': 'Monday, Wednesday, and Friday from 1-3 PST.',
        'blurb':'This course will be a basic guide to applications of number theory in math competitions. Although most of it will be instructional, lectures will be supplemented with actual number theory problems from contests so students can also develop their problem solving skills and apply what they have learned. Problems in this course will range from MathCounts difficulty all the way up to the AIME. A background in Algebra is strongly recommended for this course.',
    },
    'C' : {
        'name': 'Competition Math: Probability',
        'price': '$10/hr',
        'time': 'Monday, Wednesday, and Friday from 10 AM - 12 PM PST.',
        'blurb':'In this class, we will cover and learn from David Patrick\'s Introduction to Counting and Probability, learning a variety of concepts including Combinatorics, Complementary Counting, Casework, Geometric Probability, Expected Value, the Binomial Theorem, and more. Problems in this class will range from MATHCOUNTS to AIME level difficulty, and the concepts covered can be used in various math competitions. By taking this course, one will gain a solid understanding of basic Counting and Probability, provided they work through class and homework problems with diligence.',
    },
    'E' : {
        'name': 'Intro to MathCounts',
        'price': '$10/hr',
        'time': 'Tuesday, Thursday, and Saturday from 11 AM - 1 PM PST.',
        'blurb':'In this class, we will work through MATHCOUNTS competitions of varying difficulty. Students are expected to work through a handout of MATHCOUNTS problems/competitions before class, and class will be spent going over concepts that are used to solve the given homework problems. Solutions and handouts will be provided for every MATHCOUNTS set. By signing up for this class, you will work through sets of difficult problems, which will improve your mathematical foundation and problem solving skills. An eagerness to learn and work through difficult problems is required, but a MATHCOUNTS background is not necessary.',
    },
    'D' : {
        'name': 'Intro to Debate',
        'price': '$10/hr',
        'time': 'Monday, Wednesday, and Friday from 11 AM - 1 PM PST.',
        'blurb':'This course will begin with a basic introduction to argumentation and debate. Students will immediately begin preparing their own case files, and eventually students will have practice debates against each other to develop their actual debate skills. Debates will be held in teams of 3, using the time allocations and guidelines of typical middle school debate. At the end of the course, the different styles of high school debate will be explained, and recommendations will be given on how to begin preparing for the rigors of high school debate.',
    },
    'F' : {
        'name': 'Advanced Debate',
        'price': '$10/hr',
        'time': 'Monday, Wednesday, and Friday from 2 PM - 3:30 PM PST.',
        'blurb':'Advanced Debate is aimed to further concepts that were developed in Intro Debate and help prepare students for HS debate or National Circuit debate. We will cover more complex argumentative theory as well as develop technical skills to help competitive performance. This class is not limited to students in debate and can also be an introductory step in engaging with critical theory and the argumentative process.',
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
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    user_id=db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Classes {}>'.format(self.name)

from forms import LoginForm, RegistrationForm, EmptyForm, ResetPasswordRequestForm, ResetPasswordForm

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
    form=EmptyForm()
    classeS=current_user.check_classes().all()
    return render_template ('profile.html', classlist=classeS,form=form)

@app.route('/aboutus')
def aboutus():
    return render_template ('aboutus.html')

from emails import send_password_reset_email, send_registered_email, send_unregistered_email
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/classes', methods=['GET', 'POST'])
def classes():
    form = EmptyForm()
    return render_template ('classes.html', classes=CLASSES, form=form)

@app.route('/contactus')
def contactus():
    return render_template ('contactus.html')

@app.route('/signup/<classname>', methods=['GET', 'POST'])
@login_required
def signup(classname):
    classeS=current_user.check_classes().all()
    alreadysignedup=0
    for aclass in classeS:
        if aclass.name==classname:
            alreadysignedup=1
    if alreadysignedup==0:
        flash('You have signed up for '+classname)
        c=Classes(name=classname, Client=current_user)
        db.session.add(c)
        db.session.commit()
        send_registered_email(current_user, classname)
    else:
        flash('You have already signed up for '+classname)
    return redirect(url_for('classes'))

@app.route('/unregister/<classname>', methods=['GET', 'POST'])
@login_required
def unregister(classname):
    classeS=current_user.check_classes().all()
    for aclass in classeS:
        if aclass.name==classname:
            db.session.delete(aclass)
            send_unregistered_email(current_user, classname)
    db.session.commit()
    return redirect(url_for('profile'))
@app.route('/')
def blank():
    return redirect(url_for('home'))

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