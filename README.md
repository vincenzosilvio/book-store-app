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

    sudo apt-get update
    sudo apt-get install postgresql postgresql-contrib
    sudo service postgresql start
    sudo -u postgres psql
    
    After accessing PostgreSQL, run the following commands to create and configure the database:

    Create the database:
    CREATE DATABASE book_store;
    Grant privileges to the user:
    GRANT ALL PRIVILEGES ON DATABASE book_store TO user_name;
    
    To access the book_store database:
    psql -U user_name -d book_store
    Flask Application Setup
    
    Clone the repository:
    git clone https://github.com/yourusername/bookstore-app.git
    cd bookstore-app
    
    Install Dependencies: Make sure you have Python installed. Then install the required packages by running: 
    pip install -r requirements.txt (or make install)
    
    Install Node.js and NPM for linting HTML/JS:
    sudo apt install nodejs
    sudo apt install npm
    
    Set Up Environment Variables: You'll need to add your environment variables, including the OpenAI API key, to run the app. You can add them to .env:
    OPENAI_API_KEY=your_openai_api_key
    DATABASE_URL=your_database_url
    
    Initialize the Database Migrations: Initialize Flask migrations for the database and apply migrations:
    
    
    flask db init
    flask db migrate -m "updating Book table"
    flask db upgrade
    
    Run the Application: Start the Flask development server:
        
    flask run
    The app will be available at http://localhost:5000.

    Run Tests: To run the unit tests:
    make test

    To lint your JavaScript and HTML files, use the following command:
    
    make lint-js make lint-html make lint python or make lint

    Run code
    python app.py

