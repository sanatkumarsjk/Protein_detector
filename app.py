from datetime import datetime
from make_celery import make_celery
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user


#initializing the app
app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'


#login manager
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


#db instance
db = SQLAlchemy(app)

#database classes
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Queries(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(100))
    dna = db.Column(db.String(20000), nullable=False)
    protein = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0) 
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self): 
        return '<Task %r>' % self.id


#celery for asyn calls
app.config.update(
    CELERY_BROKER_URL='amqp://localhost//',
    CELERY_RESULT_BACKEND='redis://localhost//'
)
celery = make_celery(app)


#celery task
@celery.task(name='app.check_seq')
def check_seq(new_dna, user_email):
    protein = check_protein(new_dna)
    if protein:
        new_sequence = Queries(dna=new_dna, protein=protein, email=user_email)
    else:
        new_sequence = Queries(dna=new_dna, protein="No protein found", email=user_email)
    try:
        db.session.add(new_sequence)
        db.session.commit()
        # return redirect('/query')
    except:
        return "task not added "
    # else:
    #     return redirect('/query')


#app routes
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@app.route('/query', methods = ['GET', 'POST'])
@login_required
def process_query():
    if request.method == 'POST':
        new_dna = request.form['dna']
        check_seq.delay(new_dna,current_user.email)
        return redirect('/query')
    else:
        rows = Queries.query.filter_by(email=current_user.email).order_by(Queries.date_created.desc()).all() 
        return render_template('query.html',rows=rows)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Queries.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/query')
    except:
        return "There was error in deleteing the task"

# Authentication routes
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password): 
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) 
    login_user(user, remember=remember)
    return redirect(url_for('process_query'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first() 

    if user:  
        flash('Email address already exists')
        return redirect(url_for('signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#protein check function
def check_protein(dna):
    return False
    protein_set = set(['NC_000852', 'NC_007346', 'NC_008724', 'NC_009899', 'NC_014637', 'NC_020104', 'NC_023423', 'NC_023640', 'NC_023719', 'NC_027867'])
    i = 9
    coding_dna = Seq(dna, IUPAC.unambiguous_dna)
    messenger_rna = coding_dna.transcribe()
    return str(messenger_rna.translate())
    # while i <= len(dna):
    #     if dna[i-9:i] in protein_set:
    #         return dna[i-9:i]
    #     i+=1

if __name__ == "__main__":
    app.run(debug=True)