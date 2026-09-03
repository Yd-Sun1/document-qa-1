import streamlit as st
from openai import OpenAI
from pypdf import PdfReader

api_key = st.secrets["openai_api_key"]
client = OpenAI(api_key=api_key)

language = st.sidebar.selectbox(
    "Select summary language",
    ["English", "Chinese", "Spanish", "French"]
)

summary_type = st.sidebar.selectbox(
    "Select summary type",
    [
        "100 words",
        "2 connecting paragraphs",
        "5 bullet points"
    ]
)

use_advanced_model = st.sidebar.checkbox("Use advanced model")

if use_advanced_model:
    model_to_use = "gpt-5-mini"
else:
    model_to_use = "gpt-5-nano"

if summary_type == "100 words":
    summary_instruction = "Summarize the document in approximately 100 words."

elif summary_type == "2 connecting paragraphs":
    summary_instruction = "Summarize the document in 2 connecting paragraphs."

else:
    summary_instruction = "Summarize the document in 5 bullet points."

# Show title and description.
st.title("Lab 2 - Document Summarizer")
st.write(
    "Upload a document below to generate a summary."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management

# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a PDF document",
    type="pdf"
)



if uploaded_file:

    # Process the uploaded file.
    reader = PdfReader(uploaded_file)

    document = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            document += text + "\n"
    messages = [
    {
        "role": "user",
        "content": f"""
Please summarize the following document in {language}.

{summary_instruction}

Document:
{document}
"""
    }
]
    # Generate an answer using the OpenAI API.
    stream = client.chat.completions.create(
        model=model_to_use,
        messages=messages,
        stream=True,
    )

    # Stream the response to the app using `st.write_stream`.
    st.write_stream(stream)
