import pandas as pd
from sqlalchemy import create_engine, text

# Database configuration
DATABASE_URI = "postgresql://vincenzo:password@localhost/book_store"


def test_insert_books():
    # Create a connection to the database
    engine = create_engine(DATABASE_URI)
    connection = engine.connect()

    # Test data for the 'book_test' table
    test_data = pd.DataFrame(
        {
            "id": [1000, 1001],
            "title": ["Test Book 1", "Test Book 2"],
            "author": ["Author 1", "Author 2"],
            "year_published": [2020, 2021],
            "price": [10.99, 15.99],
            "genres": ["Fiction", "Non-fiction"],
        }
    )

    try:
        # Insert test data into 'book_test' table
        test_data.to_sql("book_test", connection, if_exists="append", index=False)

        # Query the 'book_test' table to verify the insert
        inserted_data = pd.read_sql(
            "SELECT * FROM book_test WHERE id IN (1000, 1001)", connection
        )
        assert len(inserted_data) == 2  # Ensure that 2 rows were inserted

    finally:
        # Cleanup: Delete the test data after the test using text() for raw SQL execution
        connection.execute(text("DELETE FROM book_test WHERE id IN (1000, 1001)"))
        connection.commit()  # Explicitly commit the transaction after DELETE
        connection.close()
