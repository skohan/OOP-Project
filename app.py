from flask import Flask, render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column( db.Integer, nullable = False, primary_key = True )
    email = db.Column( db.String(), nullable = False, unique = True )
    password = db.Column( db.String(), nullable = False )
    name = db.Column( db.String(), nullable = False, unique = True )
    phone =  db.Column( db.String(), nullable = False, unique = True )
    adhar_card =  db.Column( db.Integer, nullable = False, unique = True )
    pan_card = db.Column( db.String(), nullable = False, unique = True )
    balance = db.Column( db.Float, nullable = False, default = 2000 )
    login_status = db.Column( db.Integer, nullable = False, default = 0)
    transactions = db.relationship( 'Transaction', backref = 'user', uselist = False)
    def __repr__(self):
        return f"(email:{self.email}, password:{self.password})"

class Transaction(db.Model):
    id = db.Column( db.Integer, nullable = False, primary_key = True )
    time  =  db.Column( db.DateTime, nullable = False, default = datetime.utcnow )
    amount = db.Column( db.Float, nullable = False )
    reciever = db.Column( db.String(), nullable = False )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return f"(time:{self.time}, amount:{self.amount}, reciever:{self.reciever})"




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        users = User.query.all()
        username = request.form.get('username')
        password = request.form.get('password')
        for user in users:
            if user.email == username:
                u = User.query.get(user.id)
                u.login_status = 1
                db.session.commit()
                return redirect(f'/home?email={u.email}')
            
        return redirect('/login')
    return render_template('login.html')


@app.route('/signup', methods = ['GET','POST'])
def signup():
    if request.method == 'POST':
        try:
            user = User(email = request.form.get('email'),
                    password = request.form.get('password'),
                    name = request.form.get('name'),
                    phone = request.form.get('phone'),
                    adhar_card = request.form.get('adhar_card'),
                    pan_card = request.form.get('pan_card'),
                    )
        except:
            return redirect('/signup')
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html')

@app.route('/home', methods = ['POST','GET'])
def home():
    email = request.args.get('email')
    user  = User.query.filter_by(email = email).first()
    if request.method == 'POST':
        if user.login_status == 1:
            return render_template('home.html', user = user)
        else:
            return redirect('/login')
    return render_template('home.html', user = user)

@app.route('/transact', methods = ['POST'])
def transact():
    user = User.query.all()

    if request.method == 'POST':
        amount  = int(request.form.get('amount'))
        if amount>0:
            sender  = User.query.filter_by(email=request.args.get('sender') ).first()
            reciever = User.query.filter_by( email = request.form.get('reciever') ).first()
            if reciever == None:
                return redirect(f"/home?email={sender.email}")
            sender.balance = sender.balance - amount
            reciever.balance = reciever.balance + amount
            db.session.commit()
    return redirect(f"/home?email={sender.email}")


if __name__ == "__main__":
    app.run(debug = True)