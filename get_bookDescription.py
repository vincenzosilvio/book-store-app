from openai import OpenAI
import os

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


# Function to fetch book description using gpt-4o-mini model
def fetch_book_description(title, author):

    print(title, author)
    prompt = (
        f"Provide a brief plot description for the book titled '{title}' by {author}."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error fetching description: {e}")
        return "Description not available."
