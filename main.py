from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flicklist:MyNewPass@localhost:8889/flicklist'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    watched = db.Column(db.Boolean)
    rating = db.Column(db.String(5))

    def __init__(self, name):
        self.name = name
        self.watched = False

    def __repr__(self):
        return '<Movie %r>' % self.name

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

@app.route("/ratings", methods = ['GET'])
def movie_ratings():
    return render_template('ratings.html', movies = get_watched_movies())

@app.route("/crossoff", methods=['POST'])
def crossoff_movie():
    crossedoff_movie_id = request.form['crossed-off-movie']
    crossedoff_movie = Movie.query.get(crossedoff_movie_id)

    crossedoff_movie.watched = True
    db.session.add(crossedoff_movie)
    db.session.commit()

    return render_template("crossoff.html", crossedoff_movie=crossedoff_movie)

@app.route("/rating-confirmation", methods=['POST'])
def rate_movie():
    rated_movie_id = request.form['rated-movie']
    rated_movie = Movie.query.get(rated_movie_id)
    rating = request.form['rating']

    if rated_movie not in get_watched_movies():
        error = "'{0}' is not in your Watched Movies List, so you cannot rate it!".format(rated_movie)

        return redirect("/?error=" + error)

    if rating not in ["*", "**", "***", "****", "*****"]:
        error = "'{0}' is not a rating, please give {1} some stars".format(rating, rated_movie.name)

        return redirect("/?error=" + error)

    rated_movie.rating = rating
    db.session.add(rated_movie)
    db.session.commit()

    return render_template('rating-confirmation.html', rated_movie = rated_movie.name, rating = rating)

@app.route("/add", methods=['POST'])
def add_movie():
    new_movie_name = request.form['new-movie']

    if (not new_movie_name) or (new_movie_name.strip() == ""):
        error = "Please specify the movie you want to add."
        return redirect("/?error=" + error)

    if new_movie_name in terrible_movies:
        error = "Trust me, you don't want to add '{0}' to your Watchlist".format(new_movie_name)
        return redirect("/?error=" + error)

    new_movie = Movie(new_movie_name)
    db.session.add(new_movie)
    db.session.commit()
    return render_template('add-confirmation.html', new_movie=new_movie)

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    return render_template('edit.html', watchlist=get_current_watchlist(), error=encoded_error)

if __name__ == "__main__":
    app.run()
