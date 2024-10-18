#Book Store Web Application with AI Integration

##
    This project is a simple web application for managing a book store. It supports basic CRUD (Create, Read, Update, Delete) operations, filtering and sorting of books, and integrates an AI-based recommendation system using OpenAI's API and FAISS for efficient book retrieval.

### Features
    CRUD Operations: Manage the book collection with create, read, update, and delete functionality.
    Book Sorting and Filtering: Sort books based on different attributes, and filter through book collections.
    Book Description Fetching: Use the /fetch_description route to retrieve detailed book descriptions.
    AI-powered Recommender System: Based on book metadata and user queries, the system suggests books using a custom Retrieval-Augmented Generation (RAG) system.
    SQL Database Integration: The app uses Flask SQLAlchemy and PostgreSQL to store book data.
    Test Suite: The project includes a set of unit tests to ensure functionality.
    Technologies Used
    Flask: Web framework used to build the backend for CRUD operations and serving HTML templates.
    FAISS: Used for similarity-based book retrieval.
    OpenAI API: Integrated for generating book recommendations based on descriptions and user queries.
    Langchain: Facilitates the AI-based book recommender system.
    PostgreSQL: Database used for storing and managing book data.

##  Installation
    PostgreSQL Installation
    To install and set up PostgreSQL, use the following commands:

''' bash
    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    sudo service postgresql start
    sudo -u postgres psql
'''
    After accessing PostgreSQL, run the following commands to create and configure the database:

Create the database:
sql
Copia codice
CREATE DATABASE book_store;
Grant privileges to the user:
sql
Copia codice
GRANT ALL PRIVILEGES ON DATABASE book_store TO user_name;
To access the book_store database:

bash
Copia codice
psql -U vincenzo -d book_store
Flask Application Setup
Clone the repository:

bash
Copia codice
git clone https://github.com/yourusername/bookstore-app.git
cd bookstore-app
Install Dependencies: Make sure you have Python installed. Then install the required packages by running:

bash
Copia codice
pip install -r requirements.txt
Install Node.js and NPM for linting HTML/JS:

bash
Copia codice
sudo apt install nodejs
sudo apt install npm
Set Up Environment Variables: You'll need to add your environment variables, including the OpenAI API key, to run the app. You can add them to .env:

makefile
Copia codice
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_database_url
Initialize the Database Migrations: Initialize Flask migrations for the database and apply migrations:

bash
Copia codice
flask db init
flask db migrate -m "updating Book table"
flask db upgrade
Run the Application: Start the Flask development server:

bash
Copia codice
flask run
The app will be available at http://localhost:5000.

Run Tests: To run the unit tests:

bash
Copia codice
pytest
Database Management
Delete rows from a table:

sql
Copia codice
DELETE FROM nome_tabella;
Drop a table:

sql
Copia codice
DROP TABLE IF EXISTS BOOK;
Linting JavaScript/HTML Files
To lint your JavaScript and HTML files, use the following command:

bash
Copia codice
make lint-js/html
API Endpoints
CRUD Operations
GET /books: Get all books in the collection.
POST /books: Add a new book to the collection.
PUT /book/<book_id>: Update a book's details.
DELETE /book/<book_id>: Delete a book from the collection.
AI-based Recommender System
GET /recommend_books: Get AI-based book recommendations.
POST /fetch_description: Retrieve the description of a specific book.
File Structure
app.py: Main application file that defines routes and handles logic.
fetch_descr.py: Fetches descriptions for books.
get_bookDescription.py: Handles logic for retrieving detailed book descriptions from a source.
insertBooks.py: Script to insert book records into the database.
rag.py: Handles the retrieval-augmented generation system for book recommendations.
test_app.py: Unit tests for app.py.
test_fetch_descr.py: Unit tests for fetch_descr.py.
test_insert_books.py: Unit tests for insertBooks.py.
Requirements
The project relies on the following packages, listed in requirements.txt:

bash
Copia codice
psycopg2-binary
flask
flask-login
flask_sqlalchemy
flask_migrate
transformers
pytest
pandas
langchain_community
langchain_openai
faiss-cpu
black
pylint
openai
