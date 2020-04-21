from flask import Flask, render_template, session, request, jsonify
from flask_session import Session
from sqlalchemy.orm import scoped_session, sessionmaker
import hashlib
import requests
from database import db

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


def user_session(username,password):
    if db.execute("SELECT * FROM user_details WHERE email = :username and password = :password", {"username": username, "password": password}).rowcount == 1:
        return True;
    else:
        return False;


@app.route("/")
def index():
    return render_template("index.html")
	
@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/signup", methods = ["POST"])
def signup():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        password = (hashlib.sha256(request.form.get("password").encode())).hexdigest()
        if name is "" or password is "" or email is "":
            raise Exception;
        if db.execute("SELECT * FROM user_details WHERE email = :username", {"username": email}).rowcount == 0:
            db.execute("INSERT INTO user_details (name, email, password) VALUES (:name, :email, :password)",{"name": name, "email":email, "password": password})
            db.commit()
            return render_template("success.html", message = "Your account is created successfully")
        else:
            return render_template("error.html", message="Email already Registered")
    except Exception as e:
        return render_template("error.html", message="Invalid URL.")
    

@app.route("/login", methods = ["POST"])
def login():
    try:
        username = request.form.get("username")
        password = (hashlib.sha256(request.form.get("password").encode())).hexdigest()
        if username is "" or password is "":
            raise Exception;
        else:
            session["username"] = username
            session["password"] = password
    except Exception as e:
        return render_template("error.html", message=("Invalid URL.",username,password))
    try:
        if not user_session(session["username"], session["password"]):
            return render_template("error.html", message="Invalid Username And Password")
        else:
            return render_template("search.html", message = "You have successfully Logged In")
    except Exception as e:
        return render_template("error.html",message = e)

@app.route("/logout", methods = ["GET","POST"])
def logout():
    session["username"] = ""
    session["password"] = ""
    return render_template("index.html",message = "Successfully Logout")

@app.route("/search", methods = ["POST"])
def search():
    if user_session(session["username"], session["password"]):
        try:
            title = request.form.get("title")
            isbn = request.form.get("isbn")
            author = request.form.get("author")
            if title is "" and isbn is "" and author is "":
                raise Exception;
        except Exception as e:
            return render_template("error.html", message=("Invalid URL."))
        if isbn is "" and author is "":
            books = db.execute("SELECT * FROM book_details WHERE title = :title", {"title": title})
        elif title is "" and author is "":
            books = db.execute("SELECT * FROM book_details WHERE isbn = :isbn", {"isbn": isbn})
        elif title is "" and isbn is "":
            books = db.execute("SELECT * FROM book_details WHERE author = :author", {"author": author})
        elif author is "":
            books = db.execute("SELECT * FROM book_details WHERE title = :title and isbn = :isbn", {"title": title,"isbn": isbn})
        elif isbn is "":
            books = db.execute("SELECT * FROM book_details WHERE title = :title and author = :author", {"title": title,"author": author})
        elif title is "":
            books = db.execute("SELECT * FROM book_details WHERE author = :author and isbn = :isbn", {"author": author,"isbn": isbn})
        else:
            books = db.execute("SELECT * FROM book_details WHERE title = :title and isbn = :isbn and author = :author", {"title": title,"isbn": isbn,"author": author})
        return render_template("search.html", books = books)
    else:
        return render_template("error.html", message = "Invalid URL!!!")
    
@app.route("/book/<string:isbn>")
def book(isbn):
    if user_session(session["username"], session["password"]):
        book = db.execute("SELECT * FROM book_details WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if book is None:
            return render_template("error.html", message="No such book.")
        try:
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "z9zVunvvovvlluqZHkTaw", "isbns": isbn}).json()
            work_rating = res["books"][0]["work_ratings_count"]
            average_rating = res["books"][0]["average_rating"]
            if db.execute("SELECT * FROM feedback WHERE isbn = :isbn and email = :username", {"isbn": isbn, "username": session["username"]}).rowcount == 0:
                try:
                    return render_template("book.html", book = book, review = "", rating=0, work_rating = work_rating, average_rating = average_rating)
                except Exception as e:
                    return render_template("error.html", message=("Invalid URL1",e))
            else:
                try:
                    feedback = db.execute("SELECT * FROM feedback WHERE isbn = :isbn and email = :username", {"isbn": isbn, "username": session["username"]}).fetchone()
                    return render_template("book.html", book = book, review = feedback.review, rating=feedback.rating, work_rating = work_rating, average_rating = average_rating)
                except Exception as e:
                    return render_template("error.html", message=("Invalid URL2",e))
        except Exception as e:
            return render_template("error.html", message=("Invalid URL.",e))
    else:
        return render_template("error.html", message = "Invalid URL!!!")

@app.route("/review/<string:isbn>", methods=["GET","POST"])
def review(isbn):
    if user_session(session["username"], session["password"]):
        book = db.execute("SELECT * FROM book_details WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if book is None:
            return render_template("error.html", message="No such book.")
        try:
            review = request.form.get("review")
            rating = request.form.get("rating")
            if review is "" and rating is "":
                raise Exception;
            try:
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "z9zVunvvovvlluqZHkTaw", "isbns": isbn}).json()
                work_rating = res["books"][0]["work_ratings_count"]
                average_rating = res["books"][0]["average_rating"]
                db.execute("INSERT INTO feedback (isbn, email, review, rating) VALUES (:isbn, :email, :review, :rating)",{"isbn": isbn, "email":session["username"], "review": review,"rating":rating})
                db.commit()
                return render_template("book.html", book = book, review = review, rating=rating, work_rating = work_rating, average_rating = average_rating)
            except Exception as e:
                return render_template("error.html", message=("Invalid URL1",e))
        except Exception as e:
            return render_template("error.html", message=("Invalid URL."))

@app.route("/api/<string:isbn>", methods=["GET","POST"])
def api(isbn):
    try:
        book = db.execute("SELECT * FROM book_details WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if book is None:
              return jsonify({"error": "Book is not found in database"}), 404
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "z9zVunvvovvlluqZHkTaw", "isbns": isbn}).json()
        review_count = res["books"][0]["reviews_count"]
        average_score = res["books"][0]["average_rating"]
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year" : book.publication_year,
            "isbn" : isbn,
            "review_count": review_count,
            "average_score": average_score
            })
    except Exception as e:
            return render_template("error.html", message=("Invalid URL.",e))

