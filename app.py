from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from forms import LoginForm

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username) 

def make_shell_context():
    return {'db': db, 'User': User}

@app.route('/home')
def home():
    return render_template ('home.html')

@app.route('/profile')
@app.route('/profile/<user>')
def profile():
    user = {'username': 'David'}
    return render_template ('profile.html', user=user)

@app.route('/aboutus')
def aboutus():
    return render_template ('aboutus.html');

@app.route('/classes')
def classes():
    return render_template ('classes.html', classes=CLASSES)

@app.route('/')
def blank():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/profile')
    return render_template('login.html', title='Sign In', form=form)