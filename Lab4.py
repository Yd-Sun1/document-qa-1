import streamlit as st
from openai import OpenAI
import sys
from pathlib import Path
from PyPDF2 import PdfReader

# Fix SQLite for ChromaDB on Streamlit Cloud
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

import chromadb


# Page title
st.title("Lab 4 -- RAG Chatbot")


# OpenAI client
client = OpenAI(
    api_key=st.secrets["openai_api_key"]
)


# Create ChromaDB client
chroma_client = chromadb.PersistentClient(
    path="./ChromaDB_for_Lab4"
)


# Read one PDF and convert it to text
def extract_text_from_pdf(pdf_path):

    text = ""

    reader = PdfReader(pdf_path)

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# Create an embedding and add the document to ChromaDB
def add_to_collection(collection, text, file_name):

    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )

    embedding = response.data[0].embedding

    collection.add(
        documents=[text],
        ids=[file_name],
        embeddings=[embedding]
    )


# Read all PDF files in the Lab-04-Data folder
def load_pdfs_to_collection(collection, folder_path):

    folder = Path(folder_path)

    pdf_files = folder.glob("*.pdf")

    for pdf_file in pdf_files:

        text = extract_text_from_pdf(pdf_file)

        file_name = pdf_file.name

        add_to_collection(
            collection,
            text,
            file_name
        )


# Create the vector database
def create_vector_db():

    collection = chroma_client.get_or_create_collection(
        name="Lab4Collection"
    )

    # Only add the PDFs if the collection is empty
    if collection.count() == 0:

        load_pdfs_to_collection(
            collection,
            "Lab-04-Data"
        )

    return collection


# Create/load the database only once during the Streamlit session
if "Lab4_VectorDB" not in st.session_state:

    st.session_state.Lab4_VectorDB = create_vector_db()


collection = st.session_state.Lab4_VectorDB

def get_relevant_context(question):

    # Create an embedding for the user's question
    response = client.embeddings.create(
        input=question,
        model="text-embedding-3-small"
    )

    query_embedding = response.data[0].embedding

    # Search ChromaDB for the 3 most relevant documents
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    # Combine the returned document text
    context = ""

    for i in range(len(results["documents"][0])):

        file_name = results["ids"][0][i]
        document_text = results["documents"][0][i]

        context += f"\nSource: {file_name}\n"
        context += document_text
        context += "\n"

    return context

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Get user input
prompt = st.chat_input("Ask a question about the courses")


if prompt:

    # Display user message
    with st.chat_message("user"):
        st.write(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Retrieve relevant information from ChromaDB
    context = get_relevant_context(prompt)

    # Instructions for the LLM
    system_message = f"""
You are a helpful course information assistant.

Use the retrieved course information below to answer the user's question.

If you use information from the retrieved course documents, clearly say
"Based on the retrieved course information" in your answer.

If the retrieved information does not contain enough information to answer
the question, say that you could not find enough information in the course documents.

Retrieved course information:

{context}
"""

    # Send the question and retrieved information to the LLM
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    answer = response.choices[0].message.content

    # Display assistant response
    with st.chat_message("assistant"):
        st.write(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )