from flask import Flask, render_template, request, url_for, redirect
app = Flask(__name__)

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


@app.route('/home')
def home():
    return render_template ('home.html')

@app.route('/profile')
@app.route('/profile/<user>')
def profile(user=None):
    user=user or "Andrew"
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
    error=None
    if request.method=='POST':
        if request.form['username']!= 'admin' or request.form['password'] != 'admin':
            error= 'Invalid Credentials. Please Try Again.'
        else:
            return redirect(url_for('profile'))
    return render_template ('login.html', error=error)