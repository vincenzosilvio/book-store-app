document.addEventListener("DOMContentLoaded", () => {
  console.log("JavaScript Loaded Successfully"); // Log to ensure JS loaded

  fetchUserBooks(); // Fetch the list of UserBooks when the page loads

  // Handle form submission for adding a new UserBook
  const addUserBookForm = document.getElementById("add-book-form");
  addUserBookForm.addEventListener("submit", function (event) {
    event.preventDefault();
    console.log("Form submission prevented, preparing to send POST request"); // Log before sending data

    const formData = new FormData(addUserBookForm);
    const userBookData = {
      title: formData.get("title"),
      author: formData.get("author"),
      year_published: parseInt(formData.get("year_published")),
      price: parseFloat(formData.get("price")),
    };

    console.log("Sending UserBook data:", userBookData); // Log the data being sent

    fetch("/user_books", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userBookData),
    })
      .then((response) => {
        console.log("Received response:", response); // Log response
        if (!response.ok) {
          throw new Error(`Failed to add UserBook. Status: ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Server response data:", data); // Log response data
        fetchUserBooks(); // Refresh the list of UserBooks
      })
      .catch((error) => {
        console.error("Error:", error);
      });

    addUserBookForm.reset();
  });

  // Handle form submission for editing a UserBook
  const editUserBookForm = document.getElementById("edit-book-form");
  editUserBookForm.addEventListener("submit", function (event) {
    event.preventDefault();

    const formData = new FormData(editUserBookForm);
    const userBookData = {
      title: formData.get("title"),
      author: formData.get("author"),
      year_published: formData.get("year_published"),
      price: parseFloat(formData.get("price")),
    };
    const userBookId = formData.get("id");

    fetch(`/user_books/${userBookId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userBookData),
    })
      .then((response) => response.json())
      .then(() => {
        fetchUserBooks(); // Refresh the list of UserBooks
        editUserBookForm.reset();
        editUserBookForm.style.display = "none"; // Hide the form after updating
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  });

  // More JavaScript code can go here if needed.
});

// Fetch and display the list of UserBooks
function fetchUserBooks(queryString = "") {
  console.log("Running fetchUserBooks.js");

  // Make a GET request with the query string
  fetch(`/user_books${queryString}`)
    .then((response) => response.json())
    .then((data) => {
      const userBooksList = document.getElementById("books-list");
      userBooksList.innerHTML = "";

      // Add the UserBooks to the HTML table
      data.forEach((userBook) => {
        userBooksList.innerHTML += `
            <tr>
              <td><a href="/book/${userBook.id}">${userBook.title}</a></td>
              <td>${userBook.author}</td>
              <td>${userBook.year_published}</td>
              <td>${userBook.price}</td>
              <td>
                <button class="delete" onclick="deleteUserBook(${userBook.id})">Delete</button>
                <button class="edit" onclick="editUserBook(${userBook.id}, '${userBook.title}', '${userBook.author}', ${userBook.year_published}, ${userBook.price})">Edit</button>
              </td>
            </tr>
          `;
      });
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Delete a UserBook by ID
function deleteUserBook(id) {
  fetch(`/user_books/${id}`, { method: "DELETE" })
    .then((response) => response.json())
    .then(() => fetchUserBooks()) // Refresh the UserBook list after deletion
    .catch((error) => {
      console.error("Error:", error);
    });
}

// Edit a UserBook by ID (populate the form with UserBook details)
function editUserBook(id, title, author, year_published, price) {
  // Show the edit form and populate it with the UserBook details
  const editUserBookForm = document.getElementById("edit-book-form");
  editUserBookForm.style.display = "block";

  document.getElementById("edit-book-id").value = id; // Set the UserBook ID
  document.getElementById("edit-title").value = title;
  document.getElementById("edit-author").value = author;
  document.getElementById("edit-year_published").value = year_published;
  document.getElementById("edit-price").value = price;
}

// Search and filter UserBooks by title or author
function searchUserBooks() {
  const query = document.getElementById("search-query").value.toLowerCase();

  fetch("/user_books")
    .then((response) => response.json())
    .then((data) => {
      const userBooksList = document.getElementById("books-list");
      userBooksList.innerHTML = "";
      data
        .filter((userBook) => {
          return (
            userBook.title.toLowerCase().includes(query) ||
            userBook.author.toLowerCase().includes(query)
          );
        })
        .forEach((userBook) => {
          userBooksList.innerHTML += `
                    <tr>
                        <td>${userBook.title}</td>
                        <td>${userBook.author}</td>
                        <td>${userBook.year_published}</td>
                        <td>${userBook.price}</td>
                        <td>
                            <button class="delete" onclick="deleteUserBook(${userBook.id})">Delete</button>
                            <button class="edit" onclick="editUserBook(${userBook.id}, '${userBook.title}', '${userBook.author}', ${userBook.year_published}, ${userBook.price})">Edit</button>
                        </td>
                    </tr>
                `;
        });
    });
}

let currentSortField = "";
let currentSortDirection = "asc";

function sortUserBooks(field) {
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

  fetch(`/user_books?${queryString}`)
    .then((response) => response.json())
    .then((data) => {
      const userBooksList = document.getElementById("books-list");
      userBooksList.innerHTML = ""; // Clear the list

      // Add the sorted UserBooks to the HTML table body
      data.forEach((userBook) => {
        userBooksList.innerHTML += `
          <tr>
            <td>${userBook.title}</td>
            <td>${userBook.author}</td>
            <td>${userBook.year_published}</td>
            <td>${userBook.price}</td>
            <td>
              <button class="delete" onclick="deleteUserBook(${userBook.id})">Delete</button>
              <button class="edit" onclick="editUserBook(${userBook.id}, '${userBook.title}', '${userBook.author}', ${userBook.year_published}, ${userBook.price})">Edit</button>
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

  // Fetch the UserBooks with the query parameters
  fetchUserBooks("?" + queryString.toString());
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
