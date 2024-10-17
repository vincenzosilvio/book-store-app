from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)

import rag
import get_bookDescription


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a secure key for production use

# Configurazione database PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://vincenzo:password@localhost/book_store"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Setup SQLAlchemy e migrazioni
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# Tabella User
class User(UserMixin, db.Model):
    __tablename__ = "book_store_users"  # Use a new table name
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Tabella Book
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("book_store_users.id"), nullable=True)


# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/book/<int:book_id>", methods=["GET"])
@login_required
def book_details(book_id):
    """Fetch and display the details of a specific book."""
    book = Book.query.get_or_404(book_id)  # Get the book or return a 404 if not found
    description = get_bookDescription.fetch_book_description(book.title, book.author)  # Fetch description
    return render_template("book_details.html", book=book, description=description)

@app.route("/fetch_description/<int:book_id>", methods=["GET"])
@login_required
def fetch_description(book_id):
    # Fetch the book from the database
    book = Book.query.get_or_404(book_id)  # This will 404 if the book_id is invalid

    # Fetch the description from the LLM using the function
    description = get_bookDescription.fetch_book_description(book.title, book.author)

    # Return the description in a JSON response
    return jsonify({"description": description})


# Route per la registrazione
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            return "Username already exists. Please choose a different one."

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")


# Route per il login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("home"))
        else:
            return "Invalid credentials. Please try again."
    return render_template("login.html")


# Route per il logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Route per la pagina principale
@app.route("/")
@login_required
def home():
    """Render the homepage with all books for the current user."""
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", books=books)


# Route per aggiungere un nuovo libro
@app.route("/books", methods=["POST"])
@login_required
def add_book():
    """Add a new book for the current user."""
    try:
        data = request.get_json()
        if not data:
            print("No data received")  # Debugging statement
            return jsonify({"message": "No data received"}), 400

        print("Data received:", data)  # Debugging statement

        # Create the new book object
        new_book = Book(
            title=data.get("title"),
            author=data.get("author"),
            year_published=data.get("year_published"),
            price=data.get("price"),
            user_id=current_user.id,
        )

        # Add and commit the book to the database
        db.session.add(new_book)
        db.session.commit()

        print("Book added successfully")  # Debugging statement
        return jsonify({"message": "Book added successfully!"}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        print("Error occurred:", str(e))  # Debugging statement
        return jsonify({"message": f"Database Error: {str(e)}"}), 500


# Route per ottenere tutti i libri con filtraggio e ordinamento opzionali
@app.route("/books", methods=["GET"])
@login_required
def get_books():
    """Get all books for the current user with optional filtering and sorting."""
    try:
        # Get filter values from query parameters
        price_min = request.args.get("price_min", type=float)
        price_max = request.args.get("price_max", type=float)
        year_min = request.args.get("year_min", type=int)
        year_max = request.args.get("year_max", type=int)

        # Get sorting parameters
        sort_field = request.args.get("sort_field", default="id", type=str)
        sort_direction = request.args.get("sort_direction", default="asc", type=str)

        # Start with all books for the current user
        books_query = Book.query.filter_by(user_id=current_user.id)

        # Apply price filters if present
        if price_min is not None:
            books_query = books_query.filter(Book.price >= price_min)
        if price_max is not None:
            books_query = books_query.filter(Book.price <= price_max)

        # Apply year filters if present
        if year_min is not None:
            books_query = books_query.filter(Book.year_published >= year_min)
        if year_max is not None:
            books_query = books_query.filter(Book.year_published <= year_max)

        # Apply sorting
        if sort_field in ["title", "author", "year_published", "price"]:
            if sort_direction == "asc":
                books_query = books_query.order_by(getattr(Book, sort_field).asc())
            else:
                books_query = books_query.order_by(getattr(Book, sort_field).desc())

        # Execute the query and retrieve the books
        books = books_query.all()

        # Format books into a list of dictionaries
        books_data = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "year_published": book.year_published,
                "price": book.price,
                "user_id": book.user_id,
            }
            for book in books
        ]
        return jsonify(books_data)

    except SQLAlchemyError as e:
        return jsonify({"message": f"Database Error: {str(e)}"}), 500



# Route per modificare un libro esistente
@app.route("/books/<int:book_id>", methods=["PUT"])
@login_required
def update_book(book_id):
    """Update an existing book."""
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"message": "Book not found"}), 404

    if book.user_id != current_user.id:
        print("Unauthorized to update this book")  # Debugging statement
        return jsonify({"message": "Unauthorized to update this book"}), 403

    try:
        data = request.get_json()
        book.title = data.get("title", book.title)
        book.author = data.get("author", book.author)
        book.year_published = data.get("year_published", book.year_published)
        book.price = data.get("price", book.price)
        db.session.commit()
        print("Book updated successfully")  # Debugging statement
        return jsonify({"message": "Book updated successfully!"})
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500


# Route to delete a book
@app.route("/books/<int:book_id>", methods=["DELETE"])
@login_required
def delete_book(book_id):
    """Delete a book by its ID."""
    book = Book.query.get(book_id)
    if book is None:
        return jsonify({"message": "Book not found"}), 404

    # Check if the current user is allowed to delete the book
    if book.user_id != current_user.id:
        return jsonify({"message": "Unauthorized to delete this book"}), 403

    try:
        db.session.delete(book)
        db.session.commit()
        print("Book deleted successfully")  # Debugging statement
        return jsonify({"message": "Book deleted successfully!"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500


# Route for get recommdender.html
@app.route("/recommender", methods=["GET"])
@login_required
def recommender_page():
    return render_template("recommender.html")


# Route for recommendations
@app.route("/recommender", methods=["POST"])
@login_required
def recommender():
    try:
        # Get the query from the frontend
        data = request.get_json()
        query = data.get("query", "")

        if not query:
            return jsonify({"message": "Query not provided"}), 400

        # Run the RAG system and get recommendations
        recommendations = rag.get_book_recommendations(query)

        # Return the recommendation as a JSON response
        return jsonify({"recommendation": recommendations})

    except Exception as e:
        print("Error during recommendation:", str(e))
        return jsonify({"message": "Error occurred during recommendation"}), 500


@app.route("/get_recommendations", methods=["POST"])
@login_required
def get_recommendations():
    try:
        # Get the query from the frontend
        data = request.get_json()
        query = data.get("query", "")

        if not query:
            return jsonify({"message": "Query not provided"}), 400

        # Run the RAG system and get recommendations
        recommendations = rag.get_book_recommendations(query)

        # Return the recommendation as a JSON response
        return jsonify({"recommendation": recommendations})

    except Exception as e:
        print("Error during recommendation:", str(e))
        return jsonify({"message": "Error occurred during recommendation"}), 500


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
