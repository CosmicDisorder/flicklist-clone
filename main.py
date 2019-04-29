from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import cgi

app = Flask(__name__)
app.config['DEBUG'] = True      # displays runtime errors in the browser, too
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flicklist-clone:beproductive@localhost:8889/flicklist-clone'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
       
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.email

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    watched = db.Column(db.Boolean)
    rating = db.Column(db.String(6))

    def __init__(self, name):
        self.name = name
        self.watched = False

    def __repr__(self):
        return '<Movie %r>' % self.name

# a list of movie names that nobody should have to watch
terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives",
    "Starship Troopers"
]

def get_current_watchlist():
    return Movie.query.filter_by(watched=False).all()

def get_watched_movies():
    return Movie.query.filter_by(watched=True).all()


@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method =='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and password == user.password:
            session['email'] = email
            flash("Welcome back, {0}".format(user.email), "success")
            return redirect("/")
        else:
            flash("User password is incorrect or user doesn't exist", "error")
        
    return render_template("login.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            if not is_email(email): 
                flash('zoiks! "' + email + '" does not seem like an email address')
                return redirect('/register')
            if verify == password:
                user = User(email=email, password=password)
                db.session.add(user)
                db.session.commit()
                session['user'] = user.email
                return redirect("/")
            flash("whoopsiedoda, yer passwords aren't matchin'", "error")
        else:
            flash("big oof dog, yer already registered", "error")
    return render_template('register.html')


def is_email(string):
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST'])
def logout():
    del session['email']
    flash("you have been logged out", "success")
    return redirect("/")

@app.route("/rating-confirmation", methods=['POST'])
def rate_movie():
    movie_id = request.form['movie_id']
    rating = request.form['rating']

    movie = Movie.query.get(movie_id)
    movie.rating = rating
    db.session.add(movie)
    db.session.commit()

    return render_template('rating-confirmation.html', movie=movie, rating=rating)

@app.route("/ratings", methods=['GET'])
def movie_ratings():
    return render_template('ratings.html', movies = get_watched_movies())


@app.route("/crossoff", methods=['POST'])
def crossoff_movie():
    crossed_off_movie_id = request.form['crossed-off-movie']

    crossed_off_movie = Movie.query.get(crossed_off_movie_id)
    if not crossed_off_movie:
        flash("error=Attempt to watch a movie unknown to this database", "error")
        return redirect("/")

    crossed_off_movie.watched = True
    db.session.add(crossed_off_movie)
    db.session.commit()
    return render_template('crossoff.html', crossed_off_movie=crossed_off_movie)

@app.route("/add", methods=['POST'])
def add_movie():
    new_movie_name = request.form['new-movie']

    if (not new_movie_name) or (new_movie_name.strip() == ""):
        flash("Please specify the movie you want to add.", "error")
        return redirect("/")

    # if the user wants to add a terrible movie, redirect and tell them the error
    if new_movie_name in terrible_movies:
        flash("Trust me, you don't want to add '{0}' to your Watchlist".format(new_movie_name), "error")
        return redirect("/")

    movie = Movie(new_movie_name)
    db.session.add(movie)
    db.session.commit()
    return render_template('add-confirmation.html', movie=movie)

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    return render_template('edit.html', watchlist=get_current_watchlist(), error=encoded_error and cgi.escape(encoded_error, quote=True))

# TODO 5: modify this function to rely on a list of endpoints that users can visit without being redirected.
#         It should contain 'register' and 'login'.
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if (request.endpoint not in allowed_routes) and ('email' not in session):
        flash("Please log in", "errror")
        return redirect("/login")

app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RU'

if __name__ == "__main__":
    app.run()
