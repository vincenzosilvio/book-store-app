document.addEventListener("DOMContentLoaded", () => {
  console.log("JavaScript Loaded Successfully"); // Log to ensure JS loaded

  fetchBooks(); // Fetch the list of books when the page loads

  // Handle form submission for adding a new book
  const addBookForm = document.getElementById("add-book-form");
  addBookForm.addEventListener("submit", function (event) {
    event.preventDefault();
    console.log("Form submission prevented, preparing to send POST request"); // Log before sending data

    const formData = new FormData(addBookForm);
    const bookData = {
      title: formData.get("title"),
      author: formData.get("author"),
      year_published: parseInt(formData.get("year_published")),
      price: parseFloat(formData.get("price")),
    };

    console.log("Sending book data:", bookData); // Log the data being sent

    fetch("/books", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bookData),
    })
      .then((response) => {
        console.log("Received response:", response); // Log response
        if (!response.ok) {
          throw new Error(`Failed to add book. Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Server response data:", data); // Log response data
        fetchBooks(); // Refresh the list of books
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    addBookForm.reset();
  });

  document.addEventListener("DOMContentLoaded", () => {
    const suggestionsForm = document.getElementById("suggestions-form");

    suggestionsForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent default form submission

      const query = document.getElementById("query").value;

      // Make a POST request to the backend with the user's query
      fetch("/recommender", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query }),
      })
        .then((response) => response.json())
        .then((data) => {
          // Display the recommendation result
          document.getElementById("recommendation-result").innerText =
            data.recommendation;
        })
        .catch((error) => {
          console.error("Error:", error);
        });
    });
  });

  // Handle form submission for editing a book
  const editBookForm = document.getElementById("edit-book-form");
  editBookForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(editBookForm);
    const bookData = {
      title: formData.get("title"),
      author: formData.get("author"),
      year_published: formData.get("year_published"),
      price: parseFloat(formData.get("price")),
    };
    const bookId = formData.get("id");

    fetch(`/books/${bookId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(bookData),
    })
      .then((response) => response.json())
      .then(() => {
        fetchBooks(); // Refresh the list of books
        editBookForm.reset();
        editBookForm.style.display = "none"; // Hide the form after updating
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

  // More JavaScript code can go here if needed.
});

// Fetch and display the list of books
function fetchBooks(queryString = "") {
  console.log("Running fetchBooks.js");

  // Make a GET request with the query string
  fetch(`/books${queryString}`)
    .then((response) => response.json())
    .then((data) => {
      const booksList = document.getElementById("books-list");
      booksList.innerHTML = "";

      // Add the books to the HTML table
      data.forEach((book) => {
        booksList.innerHTML += `
            <tr>
              <td><a href="/book/${book.id}">${book.title}</a></td>
              <td>${book.author}</td>
              <td>${book.year_published}</td>
              <td>${book.price}</td>
              <td>
                <button class="delete" onclick="deleteBook(${book.id})">Delete</button>
                <button class="edit" onclick="editBook(${book.id}, '${book.title}', '${book.author}', ${book.year_published}, ${book.price})">Edit</button>
              </td>
            </tr>
          `;
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}


// Delete a book by ID
function deleteBook(id) {
  fetch(`/books/${id}`, { method: "DELETE" })
    .then((response) => response.json())
    .then(() => fetchBooks()) // Refresh the book list after deletion
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Edit a book by ID (populate the form with book details)
function editBook(id, title, author, year_published, price) {
  // Show the edit form and populate it with the book details
  const editBookForm = document.getElementById("edit-book-form");
  editBookForm.style.display = "block";

  document.getElementById("edit-book-id").value = id; // Set the book ID
  document.getElementById("edit-title").value = title;
  document.getElementById("edit-author").value = author;
  document.getElementById("edit-year_published").value = year_published;
  document.getElementById("edit-price").value = price;
}

// Search and filter books by title or author
function searchBooks() {
  const query = document.getElementById("search-query").value.toLowerCase();

  fetch("/books")
    .then((response) => response.json())
    .then((data) => {
      const booksList = document.getElementById("books-list");
      booksList.innerHTML = "";
      data
        .filter((book) => {
          return (
            book.title.toLowerCase().includes(query) ||
            book.author.toLowerCase().includes(query)
          );
        })
        .forEach((book) => {
          booksList.innerHTML += `
                    <tr>
                        <td>${book.title}</td>
                        <td>${book.author}</td>
                        <td>${book.year_published}</td>
                        <td>${book.price}</td>
                        <td>
                            <button class="delete" onclick="deleteBook(${book.id})">Delete</button>
                            <button class="edit" onclick="editBook(${book.id}, '${book.title}', '${book.author}', ${book.year_published}, ${book.price})">Edit</button>
                        </td>
                    </tr>
                `;
        });
    });
}

let currentSortField = "";
let currentSortDirection = "asc";

function sortBooks(field) {
  // Invert the sort direction if sorting by the same field
  if (currentSortField === field) {
    currentSortDirection = currentSortDirection === "asc" ? "desc" : "asc";
  } else {
    currentSortField = field;
    currentSortDirection = "asc"; // Default to ascending when a new field is selected
  }

  // Make a GET request with the sorting query parameters
  const queryString = new URLSearchParams({
    sort_field: currentSortField,
    sort_direction: currentSortDirection,
  });

  fetch(`/books?${queryString}`)
    .then((response) => response.json())
    .then((data) => {
      const booksList = document.getElementById("books-list");
      booksList.innerHTML = ""; // Clear the list

      // Add the sorted books to the HTML table body
      data.forEach((book) => {
        booksList.innerHTML += `
          <tr>
            <td>${book.title}</td>
            <td>${book.author}</td>
            <td>${book.year_published}</td>
            <td>${book.price}</td>
            <td>
              <button class="delete" onclick="deleteBook(${book.id})">Delete</button>
              <button class="edit" onclick="editBook(${book.id}, '${book.title}', '${book.author}', ${book.year_published}, ${book.price})">Edit</button>
            </td>
          </tr>
        `;
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}


// Function to apply filters
function applyFilters() {
  console.log("Applying filters...");

  const priceMin = document.getElementById("price-min").value;
  const priceMax = document.getElementById("price-max").value;
  const yearMin = document.getElementById("year-min").value;
  const yearMax = document.getElementById("year-max").value;

  // Construct the query string based on the filter values
  let queryString = new URLSearchParams();
  if (priceMin) queryString.append("price_min", priceMin);
  if (priceMax) queryString.append("price_max", priceMax);
  if (yearMin) queryString.append("year_min", yearMin);
  if (yearMax) queryString.append("year_max", yearMax);

  // Fetch the books with the query parameters
  fetchBooks("?" + queryString.toString());
}

// Reset filters and reload the page without any query parameters
function resetFilters() {
  // Reset the form values
  document.getElementById("year-min").value = "";
  document.getElementById("year-max").value = "";
  document.getElementById("price-min").value = "";
  document.getElementById("price-max").value = "";

  // Reload the page to show all books without any filters
  fetchBooks();
}
