from flask import Flask, request, redirect, render_template
import cgi

app = Flask(__name__)

app.config['DEBUG'] = True

terrible_movies = [
    "Gigli",
    "Star Wars Episode 1: Attack of the Clones",
    "Paul Blart: Mall Cop 2",
    "Nine Lives",
    "Starship Troopers"
]

current_watchlist = [
    "Star Wars", 
    "Minions", 
    "Freaky Friday", 
    "My Favorite Martian"
]

watched_movies = [
    "Men in Black",
    "Jaws",
    "Captain Marvel",
    "Clerks"
]

def get_current_watchlist():
    return current_watchlist

def get_watched_movies():
    return watched_movies

@app.route("/ratings", methods=['GET'])
def movie_ratings():
    return render_template("ratings.html", ratings=ratings)

@app.route("/crossoff", methods=['POST'])
def crossoff_movie():
    crossed_off_movie = request.form['crossed-off-movie']

    if crossed_off_movie not in get_current_watchlist():
        error = "'{0}' is not in your Watchlist, no dice broseph".format(crossed_off_movie)
        
        return redirect("/?error=" + error)
    
    return render_template('crossoff.html', crossed_off_movie=crossed_off_movie)

@app.route("/add", methods =['POST'])
def add_movie():
    new_movie = request.form['new-movie']

    if (not new_movie) or (new_movie.strip() == ""):
        error = "Please specificy which movie."
        return redirect("/?error=" + error)
    
    if new_movie in terrible_movies:
        error = "Trust me, '{0}' is not the one you want.".format(new_movie)
        return redirect("/?error=" + error)
    
    new_movie_escaped = cgi.escape(new_movie, quote=True)

    return render_template('add-confirmation.html', movie=new_movie_escaped)

@app.route("/")
def index():
    encoded_error = request.args.get("error")
    return render_template('edit.html', watchlist=get_current_watchlist(), error=encoded_error and cgi.escape(encoded_error, quote=True))

app.run()