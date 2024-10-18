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


# Tabella User registrati allo store digitale
class User(UserMixin, db.Model):
    __tablename__ = "book_store_users"  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Tabella UserBooks che indica quali libri possiede un utente
class UserBooks(db.Model):
    __tablename__ = "book_users"  
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("book_store_users.id"), nullable=True)


# Tabella dei libri raccolti dallo store digitale
class Book(db.Model):
    __tablename__ = "book"  # Table name
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    genres = db.Column(db.String(255), nullable=True)


# Login manager user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Route per la pagina dell'inventario
@app.route("/inventory", methods=["GET"])
@login_required
def inventory():
    """Fetch and display all available books in the inventory."""
    books = Book.query.all() # Get all books from the Book table
    return render_template("inventory.html", books=books)

#Route per aggiungere un libro alla collezione dell'utente
@app.route("/add_to_collection/<int:book_id>", methods=["POST"])
@login_required
def add_to_collection(book_id):
    """Add a book to the current user's collection."""

    # Check if the book exists in the inventory
    book = Book.query.get_or_404(book_id)

    # Check if the current user already has the book in their collection (UsersBooks table)
    existing_entry = UserBooks.query.filter_by(
        user_id=current_user.id, id=book_id
    ).first()

    if existing_entry:  # If the book is already in the user's collection
        return jsonify({"message": "Book is already in your collection"}), 400

    # Create a new entry in the UsersBooks table to link the book to the current user
    new_entry = UserBooks(
        user_id=current_user.id,
        id=book_id,
        title=book.title,
        author=book.author,
        year_published=book.year_published,
        price=book.price,
    )

    try:
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Book added to your collection!"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database Error: {str(e)}"}), 500

#Route per la pagina dei dettagli di un libro
@app.route("/book/<int:book_id>", methods=["GET"])
@login_required
def book_details(book_id):
    """Fetch and display the details of a specific book."""
    book = UserBooks.query.get_or_404(
        book_id
    )  # Get the book or return a 404 if not found
    # description = get_bookDescription.fetch_book_description(book.title, book.author)  # Fetch description
    return render_template("book_details.html", book=book)

#Route per la ottenere la descrizione da inserire in book_details.html
@app.route("/fetch_description/<int:book_id>", methods=["GET"])
@login_required
def fetch_description(book_id):
    # Fetch the book from the database
    book = UserBooks.query.get_or_404(
        book_id
    )  # This will 404 if the book_id is invalid

    # Fetch the description from the LLM using the function
    description = get_bookDescription.fetch_book_description(book.title, book.author)

    # Return the description in a JSON response
    return jsonify({"description": description})


# Route per la registrazione di un nuovo utente
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

#Route per la pagina di login
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
            return jsonify({"success": False, "message": "Invalid credentials"}), 400
    return render_template("login.html")


# Route per il logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Route per il menù principale
@app.route("/")
@login_required
def home():
    """Render the homepage with all books for the current user."""
    books = UserBooks.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", books=books)


# Route per aggiungere un nuovo libro
@app.route("/user_books", methods=["POST"])
@login_required
def add_book():
    """Add a new book for the current user and to the inventory if it doesn't exist."""

    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        # Check if the book already exists in the inventory (Book table)
        existing_book = Book.query.filter_by(
            title=data.get("title"), author=data.get("author")
        ).first()

        if existing_book:
            # If the book exists, use its book_id
            book_id = existing_book.id
            print("Book already exists in the inventory")  # Debugging statement
        else:
            # If the book does not exist, insert it into the Book table

            print("Book does not exist in the inventory")  # Debugging statement
            # Get the highest current book_id and increment it
            max_book = Book.query.order_by(Book.id.desc()).first()
            new_book_id = (
                (max_book.id + 1) if max_book else 1
            )  # Start at 1 if no books exist

            # Create a new book entry in the Book table
            new_book_in_inventory = Book(
                id=new_book_id,
                title=data.get("title"),
                author=data.get("author"),
                year_published=data.get("year_published"),
                price=data.get("price"),
                genres=data.get("genres"),  # Assuming genres are present in the request
            )

            # Add the new book to the Book table
            db.session.add(new_book_in_inventory)
            db.session.commit()

            # Set book_id to the newly created book's ID
            book_id = new_book_in_inventory.id

        # Check if the book is already in the user's collection (UserBooks table)
        existing_user_book = UserBooks.query.filter_by(
            user_id=current_user.id, id=book_id
        ).first()

        if existing_user_book:
            return (
                jsonify(
                    {"success": False, "message": "Book is already in your collection"}
                ),
                400,
            )

        # Add the book to the user's collection (UserBooks table)
        new_user_book = UserBooks(
            user_id=current_user.id,
            id=book_id,
            title=data.get("title"),
            author=data.get("author"),
            year_published=data.get("year_published"),
            price=data.get("price"),
        )

        # Add the new book to the UserBooks table
        db.session.add(new_user_book)
        db.session.commit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Book added to your collection and inventory!",
                }
            ),
            201,
        )

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Database Error: {str(e)}"}), 500


# Route per ottenere tutti i libri di un utente con filtraggio e ordinamento opzionali
@app.route("/user_books", methods=["GET"])
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
        books_query = UserBooks.query.filter_by(user_id=current_user.id)

        # Apply price filters if present
        if price_min is not None:
            books_query = books_query.filter(UserBooks.price >= price_min)
        if price_max is not None:
            books_query = books_query.filter(UserBooks.price <= price_max)

        # Apply year filters if present
        if year_min is not None:
            books_query = books_query.filter(UserBooks.year_published >= year_min)
        if year_max is not None:
            books_query = books_query.filter(UserBooks.year_published <= year_max)

        # Apply sorting
        if sort_field in ["title", "author", "year_published", "price"]:
            if sort_direction == "asc":
                books_query = books_query.order_by(getattr(UserBooks, sort_field).asc())
            else:
                books_query = books_query.order_by(
                    getattr(UserBooks, sort_field).desc()
                )

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
@app.route("/user_books/<int:book_id>", methods=["PUT"])
@login_required
def update_book(book_id):
    """Update an existing book."""
    book = UserBooks.query.get(book_id)
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


# Route per eliminare un libro
@app.route("/user_books/<int:book_id>", methods=["DELETE"])
@login_required
def delete_book(book_id):
    """Delete a book by its ID."""
    book = UserBooks.query.get(book_id)
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


# Route per caricare la pagina delle raccomandazioni
@app.route("/recommender", methods=["GET"])
@login_required
def recommender_page():
    return render_template("recommender.html")

#Route per ottenere le raccomandazioni di libri
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
