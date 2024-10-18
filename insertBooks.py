import pandas as pd
import random
from sqlalchemy import create_engine

#Script that adds 100 books to the book database

# Load books data from CSV
df = pd.read_csv("books.csv")  

# Rename columns to match the database schema
books_data = df[["Book", "Author", "Genres"]].head(100)  
books_data.columns = ["title", "author", "genres"]  # Rename columns

# Add year_published and price columns
books_data["year_published"] = [
    random.randint(1950, 2023) for _ in range(100)
]  # Random year between 1950 and 2023
books_data["price"] = [
    round(random.uniform(5.0, 50.0), 2) for _ in range(100)
]  # Random price between 5 and 50

# Add a unique id starting from 1000
books_data["id"] = range(1, 1 + len(books_data))  # Start id from 1000

# Reorder columns to match the database table
books_data = books_data[["id", "title", "author", "year_published", "price", "genres"]]

# Database configuration
DATABASE_URI = "postgresql://vincenzo:password@localhost/book_store"  # Update with your credentials

# Create a database engine
engine = create_engine(DATABASE_URI)

# Insert data into the 'book' table
books_data.to_sql("book", engine, if_exists="append", index=False)

print("Books successfully added!")
