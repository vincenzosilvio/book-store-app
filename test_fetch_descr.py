from get_bookDescription import fetch_book_description
from unittest.mock import patch, MagicMock


# Mock the API call that fetches book descriptions
@patch("get_bookDescription.client.chat.completions.create")
def test_fetch_book_description(mock_completion):
    # Set up the mock object
    mock_response = MagicMock()

    # Set the nested attributes of the mock to match the object structure
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked description"

    # Set the mock to return this mock object
    mock_completion.return_value = mock_response

    # Call the function under test (this should now use the mock)
    title = "Test Book"
    author = "Test Author"
    description = fetch_book_description(title, author)

    # Assert that the description returned matches the mocked one
    assert description == "Mocked description"
