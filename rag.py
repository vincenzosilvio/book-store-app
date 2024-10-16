import os
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain import hub
import time

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# Function to initialize the system (embedding model, vector store, etc.)
def initialize_rag_system():
    # Load your CSV file
    loader = CSVLoader("books.csv")
    documents = loader.load()

    # Create embeddings for your documents or load from disk if available
    embedding_model = OpenAIEmbeddings()

    # Check if the FAISS index already exists
    if os.path.exists("faiss_index"):
        print("Loading FAISS index from disk...")
        # Load FAISS index from disk
        vector_store = FAISS.load_local(
            "faiss_index", embedding_model, allow_dangerous_deserialization=True
        )
    else:
        print("Creating FAISS index...")
        # If FAISS index doesn't exist, create it
        vector_store = FAISS.from_documents(documents, embedding_model)
        vector_store.save_local("faiss_index")

    # Set up the retriever using the FAISS vector store's retriever interface
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.5}
    )

    # Load the custom prompt from the hub
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    # Set up the LLM
    llm = ChatOpenAI(
        model_name="gpt-4o-mini", openai_api_key=os.environ["OPENAI_API_KEY"]
    )

    # Create a chain that combines the LLM and the retrieval prompt
    combine_docs_chain = create_stuff_documents_chain(llm, retrieval_qa_chat_prompt)

    # Create the final retrieval chain
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    return retrieval_chain


# Function to get book recommendations dynamically
def get_book_recommendations(query):
    """Run the RAG system to get recommendations for the provided query."""
    retrieval_chain = initialize_rag_system()

    start_time = time.time()
    # Run the query through the retrieval chain
    response = retrieval_chain.invoke({"input": query})
    end_time = time.time()

    print(f"Time taken to retrieve answer: {end_time - start_time:.2f} seconds")
    return response["answer"]
